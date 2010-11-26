#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import logging
import markdown2
import os
import pprint

from barenaked import base
from barenaked import constants
from barenaked import utils


LOGGER = logging.getLogger(constants.app_name)

class Parser(base.BareNaked):

    def __init__(self):
        base.BareNaked.__init__(self)

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        parser.add_argument('--output', help='Overrides the "output" directive from the config file')
        parser.add_argument('--all', action='store_true', help='(Re-)Parse all the entries in the input tree (may take a while)')
        parser.add_argument('--entry', type=int, help='Entry to parse')
        parser.add_argument('--unparsed', action='store_true', help='Parse the unparsed entries')

    def process_args(self, args):
        pprint.pprint(args.output)

    def parse_entries(self, entry_list={}):
        #md2 = Markdown()
        LOGGER.debug('Will parse %d entries' % len(entry_list))
        for guid, entry in entry_list.items():
            output = os.path.join(self.config['output'], '%s.html' % entry['path'])
            self.stats['entry_list'][guid]['parsed'] = True

    def run(self):
        if not 'output' in self.config.keys():
            raise UndefinedOutputError('The parser needs an output directory')
        self.parse_entries(self.stats['entry_list'])

