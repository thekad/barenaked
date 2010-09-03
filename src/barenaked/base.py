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
format='%(filename)s:%(lineno)d - %(levelname)s: %(message)s'
if 'BARE_DEBUG' in os.environ.keys():
    logging.basicConfig(level=logging.DEBUG, format=format)
else:
    logging.basicConfig(level=logging.WARNING, format=format)
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
            self.stats = { 'last_guid': 0 }
        except Exception as e:
            LOGGER.debug(str(e))
            LOGGER.error('Cannot load the stats file at %s, this is not good' % stats_path)
            sys.exit(404)

    def run(self):
        raise NotImplementedError

    def process_args(self, args):
        pass

    def add_subparser(self, subparsers):
        pass

    def _setup_subparser(self, subparsers):
        parser = subparsers.add_parser(self.__class__.__name__.lower(),
            help='%s command help' % self.__class__.__name__.capitalize())
        return parser


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
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     description=constants.app_desc)
    parser.add_argument('-c', '--config', dest='config',
                        help='Config file, defaults to ~/.barerc',
                        default=os.path.join(os.environ['HOME'], '.barerc'))
    subparsers = parser.add_subparsers(title='Commands', dest='subparser_name')
    for module in commands.__all__:
        klass = demodule(module)
        klass = klass()
        klass.add_subparser(subparsers)
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)
    klass = demodule(args.subparser_name)
    klass = klass()
    try:
        klass.load_config(args.config)
        klass.load_stats()
        klass.process_args(args)
        klass.run()
        klass.cleanup()
    except Exception as e:
        klass.cleanup()
        LOGGER.error(str(e))

if __name__ == '__main__':
    sys.exit(main())
