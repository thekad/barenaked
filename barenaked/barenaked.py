#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import bottle
import datetime
import feedgenerator
import git
import json
import logging
import markdown2
import memcache
import os

CONF = {
    'bind_host': 'localhost',
    'bind_port': 8668,
    'bottle_reload': True,
    'git_repo': None,
    'git_branch': 'master',
    'memcached_servers': ['localhost:11211', ],
    'blog_url': None,
    'blog_title': 'A bare-naked blog',
    'blog_desc': 'Just another git-backed blog',
    'git_subdir': 'posts',
    'hash': '5832e5780c4e6341872d070aa076a419',
    'rss_limit': None,
    'recent_posts': 10,
}

format = '%(filename)s:%(lineno)d - %(levelname)s: %(message)s'
if 'BAREDEBUG' in os.environ.keys():
    logging.basicConfig(level=logging.DEBUG, format=format)
else:
    logging.basicConfig(level=logging.INFO, format=format)

LOGGER = logging.getLogger('barenaked')


def load_config():
#   Load configuration
    cfg_file = os.environ.get('BARERC', '~/.barerc')
    cfg_file = os.path.realpath(os.path.expanduser(cfg_file))
    if os.path.isfile(cfg_file):
        LOGGER.debug('Loading %s' % (cfg_file, ))
        cfg_file = open(os.path.realpath(os.path.expanduser(cfg_file)), 'rb')
        conf = json.load(cfg_file)
        cfg_file.close()
        for k, v in conf.items():
            CONF[k] = v

load_config()
if not CONF['git_repo'] or not CONF['blog_url']:
    raise KeyError('Need repo path and url')

bare = bottle.Bottle()
REPO = git.Repo(CONF['git_repo'])


def get_file_from_key(key=None):
    commit = REPO.commit(CONF['git_branch'])
    if key:
        filename = '%s/%s.markdown' % (CONF['git_subdir'], key, )
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
    html = bottle.template('404', message=message)
    return html


@bare.error(401)
def error401(message=''):
    return message


@bare.route('/restricted/<hash>/reload_config')
def reload_config(hash=None):
    "Reloads the configuration"

    if hash != CONF['hash']:
        return error401('You lack the appropriate privileges')
    load_config()
    return 'Config reloaded'


@bare.route('/restricted/<hash>/clear_cache')
def clear_cache(hash=None):
    "Clears the template cache"

    if hash != CONF['hash']:
        return error401('You lack the appropriate privileges')
    bottle.TEMPLATES.clear()
    return 'Template cache cleared'


@bare.route('/restricted/<hash>/dump_config')
def dump_config(hash=None):
    "Dumps the current loaded configuration"

    if hash != CONF['hash']:
        return error401('You lack the appropriate privileges')
    return CONF


@bare.route('/static/:path#.+#', name='static')
def serve_static(path):
    "Serve static files if not configured on the web server"

    real_path = os.path.realpath(os.path.expanduser(CONF['static']))
    LOGGER.debug('Serving static file from %s/%s' % (real_path, path,))
    return bottle.static_file(path, root=real_path)


@bare.route('/<key>')
def get_file(key=None):
    "Get the requested content from git or memcache"

    mc = memcache.Client(CONF['memcached_servers'])
    LOGGER.debug('Key: %s' % (key, ))
#   try to get from memcached
    if key:
        content = mc.get(str(key))
    else:
        content = mc.get(str('%(git_branch)s@HEAD' % CONF))
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
            dd = datetime.datetime.utcfromtimestamp(commit.authored_date)
            html = bottle.template(
                'post', title=title, message=message,
                content=content, conf=CONF, author=commit.author, pub_date=dd,
                recent=get_posts(CONF['recent_posts']),
            )
#           Set these in memory for next time
            if key:
                LOGGER.debug('Setting key %s' % (key, ))
                mc.set(str(key), html)
            else:
                key = os.path.splitext(os.path.basename(filename))[0]
                LOGGER.debug('Setting key %s' % (key, ))
                LOGGER.debug('Setting key %(git_branch)s@HEAD' % CONF)
                mc.set(str(key), html)
                mc.set(str('%(git_branch)s@HEAD' % CONF), html)
            return html
        else:
            return error404('Could not find this post')


@bare.route('/')
@bare.route('/HEAD')
def head():
    """Returns the tip of the configured head in git"""

    return get_file()


def get_posts(limit=None):
    posts = []
    kwargs = {}
    if limit:
        kwargs['max_count'] = limit
    for commit in REPO.iter_commits(CONF['git_branch'], **kwargs):
        stats = commit.stats
        filename = stats.files.keys()[0]
        title, message, blob = get_blob_data(commit, filename)
        LOGGER.debug('Adding "%s" to the feed..."' % (title,))
        slug = '.'.join(os.path.basename(filename).split('.')[:-1])
        dd = datetime.datetime.utcfromtimestamp(commit.authored_date)
        posts.append(
            {
                'title': title,
                'slug': slug,
                'blob': blob,
                'date': dd,
                'author': commit.author,
                'commit': commit,
            }
        )
    return posts


@bare.route('/rss.xml')
def rss():
    limit = CONF['rss_limit']
    LOGGER.debug('Generating %s RSS entries' % (limit or 'unlimited',))
    feed = feedgenerator.Rss201rev2Feed(
        title=CONF['blog_title'],
        link=CONF['blog_url'],
        description=CONF['blog_desc'],
    )
    for post in get_posts(limit):
        feed.add_item(
            title=post['title'],
            link='%s/%s' % (CONF['blog_url'], post['slug'],),
            description=post['blob'],
            pubdate=post['date'],
            author_name=post['author'].name,
            author_email=post['author'].email,
            unique_id=post['commit'].hexsha,
            item_copyright=post['author'].name,
        )

    LOGGER.info('Generated RSS with %d items' % (feed.num_items(),))
    return feed.writeString('utf-8')


def main():
    bottle.run(
        bare, host=CONF['bind_host'],
        port=CONF['bind_port'], reloader=CONF['bottle_reload']
    )
