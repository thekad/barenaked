#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import codecs
import logging
import os
import shutil
import sys
import tempfile
import yaml

import constants
import errors


# Logging stuff
format='%(levelname)s: %(message)s'
if 'BARE_DEBUG' in os.environ.keys():
    logging.basicConfig(level=logging.DEBUG, format=format)
else:
    logging.basicConfig(level=logging.INFO, format=format)
LOGGER = logging.getLogger(constants.app_name)

class BareNaked():

    config = None
    workdir = None
    user = None
    output = None
    stats = None

    def __init__(self):
        pass

    def setup_workdir(self):
        self.workdir = tempfile.mkdtemp(prefix=constants.app_name)
        LOGGER.debug('Work directory %s created' % self.workdir)

    def cleanup(self):
        if self.workdir:
            LOGGER.debug('Cleaning up %s' % self.workdir)
            shutil.rmtree(self.workdir)

    def load_config(self, config_file):
        '''
        Loads the properties YAML file
        '''

        try:
            LOGGER.debug('Loading %s' % config_file)
            fh = codecs.open(config_file)
            self.config = yaml.load(fh)
            fh.close()
        except Exception as e:
            LOGGER.error(str(e))
            raise errors.ConfigNotFoundError('Config file "%s" was not found or is invalid' % config_file)

    def _write_stats(self):
        stats_path = os.path.join(self.config['source'], 'stats.yaml')
        f = codecs.open(stats_path, 'wb', encoding='utf-8')
        LOGGER.debug('Writing stats.yaml')
        f.write(yaml.dump(self.stats, default_flow_style=False, encoding='utf-8'))
        f.close()

    def update_create_stats(self, guid, post_path):
        self.stats['last_entry_created'] = guid
        if post_path not in self.stats['entry_list'].values():
            stat = {}
            stat['path'] = post_path
            stat['parsed'] = False
            self.stats['entry_list'][guid] = stat
            self.stats['entry_list'].items().sort()

    def load_stats(self):
        '''Loads the general stats file'''

        stats_path = os.path.join(self.config['source'], 'stats.yaml')
        LOGGER.debug('Trying to open the stats file %s' % stats_path)
        try:
            fh = codecs.open(stats_path, 'rb')
            self.stats = yaml.load(fh)
            fh.close()
        except IOError as ioe:
            LOGGER.debug('Not found, falling back to first-post stats')
            self.stats = { 'last_entry_created': 0, 'last_entry_parsed': 0, 'entry_list': {} }
        except Exception as e:
            LOGGER.debug(str(e))
            LOGGER.error('Cannot load the stats file at %s, this is not good' % stats_path)
            sys.exit(404)
        LOGGER.debug('A total of %d items in the stats file' % len(self.stats['entry_list']))

    def run(self, args=None):
        raise NotImplementedError

    def add_subparser(self, subparsers):
        pass

    def set_args(self, args):
        self.argparse_args = args

    def _setup_subparser(self, subparsers):
        parser = subparsers.add_parser(self.__class__.__name__.lower(),
            help='%s command help' % self.__class__.__name__.capitalize())
        return parser

    def _set_author(self):
        '''Sets the user from the config file first and environment second'''

        if 'author' in self.config.keys():
            LOGGER.debug('Author from config')
            self.author = self.config['author']
            return
        if 'USER' in os.environ.keys():
            LOGGER.debug('User from env')
            self.author = os.environ['USER']
            return

def demodule(module):
    klass = ''.join([_.capitalize() for _ in module.split('_')])
    LOGGER.debug('Importing class %s from barenaked.commands.%s' % (klass, module))
    module = __import__('barenaked.commands.%s' % module, fromlist=['barenaked.commands'])
    klass = getattr(module, klass)
    return klass


def main():
    # These modules should only be imported if called from the cli
    import argparse
    import commands
    parser = argparse.ArgumentParser(description=constants.app_desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--config', dest='config',
        help='Config file',
        default=os.path.join(os.environ['HOME'], '.barerc'))
    subparsers = parser.add_subparsers(title='Commands', dest='subparser_name')
    for module in commands.__all__:
        klass = demodule(module)
        klass = klass()
        klass.add_subparser(subparsers)
        klass = None
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)
    klass = demodule(args.subparser_name)
    klass = klass()
    try:
        klass.load_config(args.config)
        klass.load_stats()
        klass.run(args)
        klass.cleanup()
    except Exception as e:
        klass.cleanup()
        LOGGER.error('Huh? %s' % e)

if __name__ == '__main__':
    sys.exit(main())

