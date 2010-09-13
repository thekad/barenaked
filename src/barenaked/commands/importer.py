#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2010, Jorge A Gallegos <kad@blegh.net>

import logging
import os
import sys

from barenaked import base
from barenaked import constants
from barenaked import errors
from barenaked import utils
from barenaked import import_drivers


LOGGER = logging.getLogger(constants.app_name)

class Importer(base.BareNaked):

    dsn = ''
    driver = ''

    def add_subparser(self, subparsers):
        '''Adds our subparser to the parent's subparser list'''

        parser = self._setup_subparser(subparsers)
        parser.add_argument('--dsn', help='Database dsn (e.g. mysql://user[:pass]@host/db)')
        parser.add_argument('--driver', help='Select your importer driver, currently: %s' %
            ','.join(import_drivers.__all__))

    def _fetch_posts(self):
        raise NotImplementedError()

    def _fetch_tags(self, guid):
        raise NotImplementedError()

    def process_args(self, args):
        self.dsn = args.dsn
        LOGGER.debug('Importer DSN: %s' % self.dsn)
        self.driver = args.driver
        LOGGER.debug('Importer Driver: %s' % self.driver)

    def run(self):
        '''Main loop'''

        if not self.driver:
            print 'Please specify a driver'
            sys.exit(1)
        if not self.dsn:
            print 'The importer needs a DSN to work with'
            sys.exit(1)
        self.load_stats()
        self.setup_workdir()
        self._set_author()
        new_guid = int(self.stats['last_entry_created']) + 1

