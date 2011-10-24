#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import codecs
import collections
import datetime
import errno
import jinja2
from jinja2 import loaders
import logging
import markdown2
import os
import PyRSS2Gen
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

    def build_feed(self, filename, title, description, items):
        LOGGER.info('Building RSS Feed %s' % (filename,))
        rss_items = []
        for item in items:
            f = '%s/%s.yaml' % (self.config['source'], item['path'])
            f = codecs.open(f)
            y = yaml.safe_load(f.read())
            f.close()
            rss_items.append(
                PyRSS2Gen.RSSItem(
                    title = y['title'],
                    link = '%s/%s.html' % (self.config['blog']['url'],
                        item['path']),
                    description = markdown2.markdown(y['body']),
                    pubDate = y['createtime']
                )
            )
        rss = PyRSS2Gen.RSS2(
            generator = '%s v%s using PyRSS2Gen' % (constants.app_name, constants.app_version),
            title = title,
            link = '%s/%s.html' % (self.config['blog']['url'], filename),
            description = description,
            lastBuildDate = datetime.datetime.now(),
            items = rss_items)
        f = codecs.open('%s/%s.xml' % (self.config['output'], filename), 'wb')
        rss.write_xml(f)
        f.close()

    def parse_entries(self, entry_list={}):
        LOGGER.debug('Will parse %d entries' % len(entry_list))
        LOGGER.debug('Loading templates from %s' % self.templates)
        tpl = self.jinja2.get_template('entry.html')
        dqs = {}
        if 'feedsize' in self.config['blog'].keys():
            feedsize = int(self.config['blog']['feedsize'])
        else:
            feedsize = 5
        for k,v in self.stats['tags'].items():
            dqs[k] = collections.deque(v, maxlen=feedsize)
        if 'feed' not in self.stats.keys():
            main_feed = collections.deque([], maxlen=feedsize)
        else:
            main_feed = collections.deque(self.stats['feed'], maxlen=feedsize)
        update_tags = set()
        for guid, entry in entry_list.items():
            ofile = os.path.join(self.output, '%s.html' % entry['path'])
            ifile = os.path.join(self.source, '%s.yaml' % entry['path'])
            LOGGER.debug('Will transform %s into %s' % (ifile, ofile))
            try:
                f = codecs.open(ifile)
                ifile = yaml.load(f)
                f.close()
            except Exception as e:
                ifile = os.path.join(self.source, '%s.yaml' % entry['path'])
                LOGGER.warn(str(e))
                LOGGER.error('File %s (entry # %d) was not parsed' % (ifile, guid))
                continue
            LOGGER.info('Writing %s' % ofile)
            file_path = os.path.dirname(ofile)
            try:
                LOGGER.debug('Creating %s' % file_path)
                os.makedirs(file_path)
            except OSError as ose:
                if ose.errno == errno.EEXIST:
                    LOGGER.debug('Already exists!')
                else:
                    raise
            content = markdown2.markdown(ifile['body'])
            ifile['body'] = content
            html = tpl.render(blog=self.config['blog'], entry=ifile)
            try:
                of = codecs.open(ofile, 'wb', encoding='utf-8')
                of.write(html)
            except Exception as e:
                LOGGER.warn(str(e))
                LOGGER.error('File %s (entry # %d) was parsed but was not written' % (ofile, guid))
#               Try to close the open file if it was opened
                try:
                    of.close(parsed)
                except:
                    pass
            self.stats['entry_list'][guid]['parsed'] = True
            self.stats['last_entry_parsed'] = guid
            main_feed.append(guid)
            for tag in ifile['tags']:
                update_tags.add(tag)
                if tag in dqs.keys():
                    dqs[tag].append(guid)
                else:
                    dqs[tag] = collections.deque([guid], maxlen=feedsize)
        self.stats['feed'] = sorted(list(set(main_feed)))
        for k,v in dqs.items():
            self.stats['tags'][k] = sorted(list(set(v)))
        if not os.path.isdir('%s/tags' % self.config['output']):
            os.makedirs('%s/tags' % self.config['output'])
        for tag in update_tags:
            items = [ self.stats['entry_list'][_] for _ in self.stats['tags'][tag] ]
            self.build_feed('tags/%s' % (tag,), '%s // %s' % (
                self.config['blog']['title'], tag), '%s feed' % tag, items)
        items = [ self.stats['entry_list'][_] for _ in main_feed ]
        self.build_feed('rss2',
            self.config['blog']['title'],
            self.config['blog']['description'],
            items
        )
        self.update_stats()

    def run(self, args):
        self.output = self.config.get('output', False)
        self.source = self.config.get('source', False)
        self.templates = self.config.get('templates', False)
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
        self.jinja2 = jinja2.Environment(loader=loaders.FileSystemLoader(self.templates))
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

