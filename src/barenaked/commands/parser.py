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
    source = None
    templates = None
    parsed = []

    def __init__(self):
        base.BareNaked.__init__(self)

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        parser.add_argument('-o', '--output', help='Overrides the "output" directive from the config file')
        parser.add_argument('-a', '--all', action='store_true', help='(Re-)Parse all the entries in the input tree (may take a while)')
        parser.add_argument('-e', '--entry', type=int, help='Entry to parse')
        parser.add_argument('-u', '--unparsed', action='store_true', help='Parse the unparsed entries')
        parser.add_argument('-l', '--list', action='store_true', help='List unparsed entries')
        parser.add_argument('-t', '--templates', help='Overrides the "templates" directive from the config file, '
                            'directory that holds the templates for parsing')

    def _update_tags(self):
        for category in self.categories:
            pass

    def _save_entry(self, guid, entry):
        """Saves a given entry"""

        ofile = os.path.join(self.output, '%s.html' % entry['path'])
        if not os.path.isdir(os.path.dirname(ofile)):
            LOGGER.debug('Creating %s' % os.path.dirname(ofile))
            try:
                os.makedirs(os.path.dirname(ofile))
            except Exception as e:
                LOGGER.debug('Failed to create %s' % os.path.dirname(ofile))
                LOGGER.error('Could not create the directory for the post #%s' % guid)
                return False

        ifile = os.path.join(self.source, '%s.yaml' % entry['path'])
        LOGGER.debug('Will transform %s into %s' % (ifile, ofile))

        try:
            f = codecs.open(ifile, 'rb', encoding='utf-8')
            ifile = yaml.load(f)
            f.close()
        except Exception, e:
            ifile = os.path.join(self.source, '%s.yaml' % entry['path'])
            LOGGER.warn(str(e))
            LOGGER.error('File %s (entry # %d) was not parsed' % (ifile, guid))
            return False

        LOGGER.info('Writing %s' % ofile)
        content = markdown2.markdown(ifile['body'])
        ifile['body'] = content
        self.__gen_parsed_entries(guid)
        ifile['previous'] = None
#       If it's not the first parsed element
        if self.parsed.index(guid):
            #ifile['previous'] = '%s/%s.html' % (self.config['blog']['url'], self.stats['entry_list'][self.parsed[self.parsed.index(guid)]]['path'])
            ifile['previous'] = '%s.html' % self.stats['entry_list'][self.parsed[self.parsed.index(guid) - 1]]['path']
            LOGGER.debug('previous is %s' % ifile['previous'])
        ifile['next'] = None
#       If it's not the last element
        if self.parsed.index(guid) < ( len(self.parsed) - 1 ):
            #ifile['next'] = '%s/%s.html' % (self.config['blog']['url'], self.stats['entry_list'][self.parsed[self.parsed.index(guid) + 2]]['path'])
            ifile['next'] = '%s.html' % self.stats['entry_list'][self.parsed[self.parsed.index(guid) + 1]]['path']
            LOGGER.debug('next is %s' % ifile['next'])
        tpl = self.tpl_env.get_template('entry.html')
        f = codecs.open(ofile, 'wb', encoding='utf-8')
        f.write(tpl.render(blog=self.config['blog'], entry=ifile, encoding='utf-8'))
        f.close()
        self.stats['entry_list'][guid]['parsed'] = True
        self.stats['last_entry_parsed'] = guid

    def __gen_parsed_entries(self, e=None):
        LOGGER.debug('Generating list of parsed entries')
        for guid, entry in self.stats['entry_list'].items():
            if entry['parsed'] and guid not in self.parsed:
                self.parsed.append(guid)
        if e and e not in self.parsed:
            self.parsed.append(e)
        self.parsed.sort()

    def parse_entries(self, entry_list={}):
        LOGGER.debug('Will parse %d entries' % len(entry_list))
        LOGGER.debug('Loading templates from %s' % self.templates)
        self.tpl_env = jinja2.Environment(loader=loaders.FileSystemLoader(self.templates))
        for guid, entry in entry_list.items():
            if self._save_entry(guid, entry):
                pass
        self._write_stats()

    def run(self, args):
        if 'output' in self.config.keys():
            self.output = self.config['output']
        if 'source' in self.config.keys():
            self.source = self.config['source']
        if 'templates' in self.config.keys():
            self.templates = self.config['templates']
        self.__gen_parsed_entries()
        if args.list:
            if self.stats['entry_list']:
                for k,v in self.stats['entry_list'].items():
                    if not v['parsed']:
                        print '%d: %s' % (int(k), v['path'])
            else:
                print '--'
            return
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

