#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2010, Jorge A Gallegos <kad@blegh.net>

import codecs
from datetime import datetime
import errno
import logging
import os
import yaml

from barenaked import base
from barenaked import constants
from barenaked import utils


LOGGER = logging.getLogger(constants.app_name)

class Importer(base.BareNaked):

    def add_subparser(self, subparsers):
        '''Adds our subparser to the parent's subparser list'''

        parser = self._setup_subparser(subparsers)
        parser.add_argument('-f', '--file', help='YAML input file', required=True)

    def save_entry(self, guid, entry):
        slug = utils.slugify(entry['title'])
        entry['guid'] = int(guid)
        date = entry['createtime']
        post_path = os.path.join(str(date.year),
            '%02d' % date.month,
            '%02d' % date.day)
        file_path = os.path.join(self.config['source'], post_path)
        LOGGER.debug('Creating the directory %s' % file_path)
        try:
            os.makedirs(file_path)
        except OSError as ose:
            if ose.errno == errno.EEXIST:
                pass
            else:
                raise
        post_path =  '%s/%s' % (post_path, slug)
        file_path = os.path.join(file_path, '%s.yaml' % slug)
        f = codecs.open(file_path, 'wb', encoding='utf-8')
        LOGGER.debug('Writing %s' % post_path)
        f.write(yaml.safe_dump(entry, explicit_start=True,
            default_flow_style=False, encoding='utf-8'))
        f.close()
        return post_path

    def run(self, args):
        '''Main loop'''

        self.load_stats()
        self.setup_workdir()
        LOGGER.info('Importing from %s' % args.file)
        try:
            fh = codecs.open(args.file, 'rb', encoding='utf-8')
            posts = yaml.load(fh.read())
            fh.close()
        except Exception as e:
            LOGGER.error(e)
            return 1
        counter = 0
        for id,entry in posts.items():
            counter += 1
            if not counter % 5:
                LOGGER.info('Imported %d entries...' % counter)
            guid = int(self.stats['last_entry_created']) + 1
            post_path = self.save_entry(guid, entry)
            self.update_create_stats(guid, str(post_path))
        self._write_stats()
        LOGGER.info('Done. Imported %d entries' % counter)

