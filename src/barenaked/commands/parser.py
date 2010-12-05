#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import codecs
import jinja2
from jinja2 import loaders
import logging
import markdown2
import os
import sys
import yaml

from barenaked import base
from barenaked import constants
from barenaked import utils


LOGGER = logging.getLogger(constants.app_name)

class Parser(base.BareNaked):

    output = None

    def __init__(self):
        base.BareNaked.__init__(self)

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        parser.add_argument('-o', '--output', help='Overrides the "output" directive from the config file')
        parser.add_argument('-s', '--source', help='Overrides the "source" directive from the config file')
        parser.add_argument('-a', '--all', action='store_true', help='(Re-)Parse all the entries in the input tree (may take a while)')
        parser.add_argument('-e', '--entry', type=int, help='Entry to parse')
        parser.add_argument('-u', '--unparsed', action='store_true', help='Parse the unparsed entries')
        parser.add_argument('-t', '--templates', help='Overrides the "templates" directive from the config file, '
                            'directory that holds the templates for parsing')

    def parse_entries(self, entry_list={}):
        LOGGER.debug('Will parse %d entries' % len(entry_list))
        LOGGER.debug('Loading templates from %s' % self.templates)
        env = jinja2.Environment(loader=loaders.FileSystemLoader(self.templates))
        tpl = env.get_template('base.html')
        print tpl
        for guid, entry in entry_list.items():
            ofile = os.path.join(self.output, '%s.html' % entry['path'])
            ifile = os.path.join(self.source, '%s.yaml' % entry['path'])
            LOGGER.debug('Will transform %s into %s' % (ifile, ofile))
            try:
                f = codecs.open(ifile)
                ifile = yaml.load(f)
                f.close()
            except Exception, e:
                ifile = os.path.join(self.source, '%s.yaml' % entry['path'])
                LOGGER.warn(str(e))
                LOGGER.error('File %s (entry # %d) was not parsed' % (ifile, guid))
                continue
            LOGGER.info('Writing %s' % ofile)
            content = markdown2.markdown(ifile['body'])
            ifile['body'] = content
            print tpl.render(blog=self.config['blog'], entry=ifile)
            self.stats['entry_list'][guid]['parsed'] = True

    def run(self, args):
        self.output = self.config.pop('output', False)
        self.source = self.config.pop('source', False)
        self.templates = self.config.pop('templates', False)
        if args.source:
            self.source = args.source
        if args.output:
            self.output = args.output
        if args.templates:
            self.templates = args.templates
        if not self.output:
            raise ValueError('The parser needs an output directory')
        if args.all:
            self.parse_entries(self.stats['entry_list'])
        elif args.unparsed:
            self.parse_entries(dict((k,v) for (k,v) in self.stats['entry_list'].items() if not v['parsed']))
        elif args.entry:
            if args.entry not in self.stats['entry_list'].keys():
                raise KeyError('The specified entry does not exist')
            self.parse_entries({ args.entry: self.stats['entry_list'][args.entry] })
        else:
            LOGGER.warn('You have to parse something, check -h for help')

