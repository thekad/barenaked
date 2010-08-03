#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

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

    def __init__(self, config_file):
        self.workdir = tempfile.mkdtemp(prefix=constants.app_name)
        LOGGER.debug('Work directory %s created' % self.workdir)
        if not self._load_config(config_file):
            self.cleanup()
            raise errors.ConfigNotFoundError('Config file "%s" was not found or is invalid' % config_file)

    def cleanup(self):
        LOGGER.debug('Cleaning up %s' % self.workdir)
        shutil.rmtree(self.workdir)

    def set_user(self, user=None):
        if user:
            self.user = user
        else:
            self.user = os.getenv('USER')

    def set_output(self, output):
        self.output = output

    def _load_config(self, config_file):
        '''
        Loads the properties YAML file
        '''

        try:
            LOGGER.debug('Loading %s' % config_file)
            fh = open(config_file)
            self.config = yaml.load(fh)
            fh.close()
            return True
        except Exception as e:
            LOGGER.warn(str(e))
            return False

def main():
    # This module should only be imported if called from the cli
    import optparse
    op = optparse.OptionParser(version=constants.app_version)
    op.add_option('-e', '--editor', dest='editor',
                  action='store_true', default=False,
                  help='Start "editor mode"')
    op.add_option('-p', '--parser', dest='parser',
                  action='store_true', default=False,
                  help='Parse the contents of the source dir')
    op.add_option('-c', '--config', dest='config',
                  default=os.path.join(os.environ['HOME'], '.barerc'),
                  help='Configuration YAML file to use (defaults to ~/.barerc)')
    op.add_option('-o', '--output', dest='output',
                  help='Overrides the output directive from the config file')
    op.add_option('-r', '--rebuild', dest='rebuild', default=False,
                  help='Rebuilds the whole site')
    op.add_option('-u', '--user', dest='user', help='Overrides the ENV user')
    #parser.add_options('-l', '--plugins')
    (options, args) = op.parse_args()

    if len(sys.argv) < 2:
        op.print_help()
        sys.exit(0)
    bn = None
    config = os.path.abspath(options.config)

    try:
        # Validate at least one mode
        if not options.editor and not options.parser:
            raise ValueError('You have to start either in editor or parser mode')
        if options.editor:
            from commands import editor
            bn = editor.Editor(config)
        if options.parser:
            from commands import parser
            bn = parser.Parser(config)
        bn.set_user(options.user)
        bn.run()
        bn.cleanup()
    except Exception as ex:
        LOGGER.error(str(ex))
        if bn:
            bn.cleanup()

if __name__ == '__main__':
    sys.exit(main())

