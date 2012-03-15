#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import bottle
import git
import json
import logging
import markdown2
import memcache
import os

CONF = {
    'host': 'localhost',
    'port': 8668,
    'reload': True,
    'branch': 'master',
    'memcached': ['localhost:11211', ],
    'repo': None,
    'url': None,
    'static': None,
    'subdir': 'posts',
    'hash': '5832e5780c4e6341872d070aa076a419',
}

format = '%(filename)s:%(lineno)d - %(levelname)s: %(message)s'
if 'BAREDEBUG' in os.environ.keys():
    logging.basicConfig(level=logging.DEBUG, format=format)
else:
    logging.basicConfig(level=logging.INFO, format=format)

LOGGER = logging.getLogger('barenaked')

# Load configuration
cfg_file = os.environ.get('BARERC', '~/.barerc')
cfg_file = os.path.realpath(os.path.expanduser(cfg_file))
if os.path.isfile(cfg_file):
    cfg_file = open(os.path.realpath(os.path.expanduser(cfg_file)), 'rb')
    conf = json.load(cfg_file)
    cfg_file.close()
    for k, v in conf.items():
        CONF[k] = v

if not CONF['repo'] or not CONF['url']:
    raise KeyError('Need repo path and url')

bare = bottle.Bottle()


def get_file_from_key(key=None):
    repo = git.Repo(CONF['repo'])
    commit = repo.commit(CONF['branch'])
    if key:
        filename = '%s/%s.markdown' % (CONF['subdir'], key, )
    else:
#       Find blob path from the tip of the configured branch
        stats = commit.stats
        filename = stats.files.keys()[0]
    return commit, filename


def get_blob_data(commit, filename):
    "Get the commit blob given a path"
    tree = None
    try:
        for c in commit.iter_items(commit.repo, commit, paths=filename):
            title = c.summary
            message = c.message
            break
        tree = commit.tree[filename]
        blob = tree.data_stream.read()
        return (title, message, blob)
    except Exception as e:
        LOGGER.error(e)
        LOGGER.warning('No git information could be found')
        return (None, None, None)


@bare.route('/favicon.ico')
def favicon():
    return error404()


@bare.error(404)
def error404(message=''):
    return message


@bare.error(401)
def error401(message=''):
    return message


@bare.route('/restricted/<hash>/clear_cache')
def clear_cache(hash=None):
    "Clears the template cache"

    if hash != CONF['hash']:
        return error401('You lack the appropriate privileges')
    bottle.TEMPLATES.clear()
    return 'Template cache cleared'


@bare.route('/<key>')
def get_file(key=None):
    "Get the requested content from git or memcache"

    mc = memcache.Client(CONF['memcached'])
    LOGGER.debug('Key: %s' % (key, ))
#   try to get from memcached
    if key:
        content = mc.get(key)
    else:
        content = mc.get('%(branch)s@HEAD' % CONF)
    if content:
        LOGGER.debug('Found content in memcache')
        return content
    else:
        commit, filename = get_file_from_key(key)
        LOGGER.debug('Commit: %s' % (commit, ))
        LOGGER.debug('Filename: %s' % (filename, ))
        title, message, blob = get_blob_data(commit, filename)
        if blob:
            content = markdown2.markdown(blob)
            html = bottle.template('post', title=title, message=message,
                content=content, conf=CONF)
#           Set these in memory for next time
            if key:
                LOGGER.debug('Setting key %s' % (key, ))
                mc.set(key, html)
            else:
                key = os.path.splitext(os.path.basename(filename))[0]
                LOGGER.debug('Setting key %s' % (key, ))
                LOGGER.debug('Setting key %(branch)s@HEAD' % CONF)
                mc.set(key, html)
                mc.set('%(branch)s@HEAD' % CONF, html)
            return html
        else:
            return error404('Could not find this post')


@bare.route('/')
@bare.route('/HEAD')
def head():
    """Returns the tip of the configured head in git"""

    return get_file()

bottle.run(bare, host=CONF['host'], port=CONF['port'], reloader=CONF['reload'])

