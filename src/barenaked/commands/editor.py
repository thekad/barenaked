#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import codecs
from datetime import datetime
import errno
import logging
import os
import subprocess
import sys
import yaml

from barenaked import base
from barenaked import constants
from barenaked import errors
from barenaked import utils


LOGGER = logging.getLogger(constants.app_name)

META_TMPL = '''---
# -*- mode: yaml; sh-basic-offset: 2; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=2 softtabstop=2 expandtab shiftwidth=2 fileencoding=utf-8

title:
createtime: %(createtime)s
author: %(user)s
# If you want to override your global comment settings, say Yes or No
comments: %(comments)s
# You can specify a list of tags here
tags:
- general
'''

class Editor(base.BareNaked):

    editor = None
    post = None
    date = None
    source = None

    def __init__(self):
        base.BareNaked.__init__(self)
        self.date = datetime.now()

    def _set_editor(self, editor=None):
        '''Sets the editor from the config file first and environment second'''

        if editor:
            self.editor = editor
            return
        if 'editor' in self.config.keys():
            LOGGER.debug('Editor from config')
            self.editor = self.config['editor']
            return
        if 'EDITOR' in os.environ.keys():
            LOGGER.debug('Editor from env')
            self.editor = os.environ['EDITOR']
            return
 
    def place_files(self):
        '''Places the meta yaml and body text files in the workdir'''

        f = os.path.join(self.workdir, 'meta.yaml')
        LOGGER.debug('Writing file %s' % f)
        meta = codecs.open(f, 'wb', encoding='utf-8')
        meta.write(META_TMPL % {
            'user': self.author,
            'createtime': self.date.isoformat(),
            'comments': self.config['blog'].get('comments', False) and 'Yes' or 'No',
        })
        meta.close()
        f = os.path.join(self.workdir, 'body.txt')
        LOGGER.debug('Writing file %s' % f)
        body = codecs.open(f, 'wb', encoding='utf-8')
        body.write('# Write your body post here')
        body.close()

    def parse_post(self):
        '''Parses the meta and body files in a single valid yaml file'''

        f = os.path.join(self.workdir, 'body.txt')
        f = codecs.open(f, 'rb', encoding='utf-8')
        body = f.read()
        f.close()
        f = os.path.join(self.workdir, 'meta.yaml')
        f = codecs.open(f, 'rb', encoding='utf-8')
        meta = f.read()
        f.close()
        self.post = yaml.load(meta)
        if not self.validate_meta(self.post):
            return False
        self.post['body'] = body
        LOGGER.debug(self.post)
        return True

    def validate_meta(self, meta):
        '''Validates the meta info for completeness'''

        if 'title' not in meta.keys() or not meta['title']:
            LOGGER.warn('A post needs a title')
            return False
        if 'author' not in meta.keys() or not meta['author']:
            LOGGER.warn('Who is writing this post? needs an author')
            return False
        post_path = os.path.join(str(self.date.year),
            '%02d' % self.date.month,
            '%02d' % self.date.day)
        posts = [ _['path'] for _ in self.stats['entry_list'].values() if _['path'].startswith(post_path) ]
        if '%s/%s' % (post_path, utils.slugify(meta['title'])) in posts:
            LOGGER.warn('There is another post written today with the same title')
            return False
        return True
        
    def save_post(self, guid):
        '''Saves the complete yaml file'''

        post_path = os.path.join(str(self.date.year),
            '%02d' % self.date.month,
            '%02d' % self.date.day)
        file_path = os.path.join(self.config['source'], post_path)
        LOGGER.debug('Creating the directory %s' % file_path)
        try:
            os.makedirs(file_path)
        except OSError as ose:
            if ose.errno == errno.EEXIST:
                pass
            else:
                raise
        self.post['guid'] = guid
        post_path =  '%s/%s' % (post_path, utils.slugify(self.post['title']))
        file_path = os.path.join(file_path, '%s.yaml' % utils.slugify(self.post['title']))
        f = codecs.open(file_path, 'wb', encoding='utf-8')
        LOGGER.debug('Writing post.yaml')
        f.write(yaml.safe_dump(self.post, explicit_start=True,
            default_flow_style=False, encoding='utf-8'))
        f.close()
        return post_path
 
    def add_subparser(self, subparsers):
        '''Adds our subparser to the parent's subparser list'''

        parser = self._setup_subparser(subparsers)
        parser.add_argument('-e', '--editor', help='Overrides the "editor" directive from the config file')

    def edit_files(self):
        '''Edit both files via self.editor'''

        files = '%(wd)s/meta.yaml %(wd)s/body.txt' % {'wd': self.workdir}
        cmd = '%s %s' % (self.editor, files)
        LOGGER.debug('Command is: %s' % cmd)
        p = subprocess.Popen(cmd, shell=True)
        LOGGER.debug('Waiting for subprocess to come back...')
        sts = os.waitpid(p.pid, 0)[1]

    def run(self, args):
        '''Main loop'''

        self._set_editor(args.editor)
        self.setup_workdir()
        LOGGER.debug(self.config)
        self._set_author()
        self.place_files()
        LOGGER.info('Running editor %s' % self.editor)
        if self.editor:
            self.edit_files()
            while not self.parse_post():
                sys.stdout.write('Your post has some errors, want to try again ("n" means abandon your post)? (Y/n)\n')
                sys.stdout.flush()
                try:
                    retry = sys.stdin.readline().rstrip('\r\n').lower()
                    if retry == '':
                        retry = 'y'
                except KeyboardInterrupt:
                    retry = 'n'
                if retry == 'y':
                    self.edit_files()
                else:
                    print 'Abandoning post'
                    self.cleanup()
                    sys.exit(2)
            guid = int(self.stats['last_entry_created']) + 1
            post_path = self.save_post(guid)
            self.stats['last_entry_created'] = guid
            stat = {}
            stat['path'] = post_path
            stat['parsed'] = False
            stat['title'] = self.post['title']
            self.stats['entry_list'][guid] = stat
            self.update_stats()
        else:
            raise errors.InvalidEditorError('Cannot fire up editor %s' % self.editor)

