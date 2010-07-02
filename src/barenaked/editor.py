#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

from datetime import datetime
import logging
import os
import subprocess

import barenaked
import constants
import errors

LOGGER = logging.getLogger(constants.app_name)

META_TMPL = """---
# -*- mode: yaml; sh-basic-offset: 2; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=2 softtabstop=2 expandtab shiftwidth=2 fileencoding=utf-8

title:
# Specify date if you don't want the file's mtime
# to be used (i.e. if this post is in the future)
# Date must be in rfc2822, i.e. date -R (TZ is ignored)
#date:
# Author username must exist in the global config file to
# be parsed (defaults to $USER)
author: %(user)s
# If you want to override your global comment settings, say Yes or No
#comments:
# You can specify a list of tags here
tags:
  - general
"""

class Editor(barenaked.BareNaked):

    editor = None
    post_date = None

    def __init__(self, config_file):
        barenaked.BareNaked.__init__(self, config_file)
        self.post_date = datetime.now()

    def set_editor(self, editor=None):
        LOGGER.debug(editor)
        if editor:
            LOGGER.debug('Editor from config')
            self.editor = editor
            return
        if 'EDITOR' in os.environ.keys():
            LOGGER.debug('Editor from env')
            self.editor = os.environ['EDITOR']
            return

    def place_files(self):
        f = os.path.join(self.workdir, 'meta.yaml')
        LOGGER.debug('Writing file %s' % f)
        meta = open(f, 'wb')
        meta.write(META_TMPL % {'user': self.user})
        meta.close()
        f = os.path.join(self.workdir, 'body.txt')
        LOGGER.debug('Writing file %s' % f)
        body = open(f, 'wb')
        body.close()

    def parse_body(self):
        f = os.path.join(self.workdir, 'body.txt')
        body = open(f, 'rb')
        body.close()

    def run(self):
        LOGGER.debug(self.config)
        if 'editor' in self.config.keys():
            self.set_editor(self.config['editor'])
        else:
            self.set_editor()
        self.place_files()
        LOGGER.info('Running editor %s' % self.editor)
        if self.editor:
            files = '%(wd)s/meta.yaml %(wd)s/body.txt' % ({'wd': self.workdir})
            cmd = '%s %s' % (self.editor, files)
            LOGGER.debug('Command is: %s' % cmd)
            p = subprocess.Popen(cmd, shell=True)
            LOGGER.debug('Waiting for subprocess to come back...')
            sts = os.waitpid(p.pid, 0)[1]
        else:
            raise errors.InvalidEditorError('Cannot fire up editor %s' % self.editor)

