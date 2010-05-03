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

# Logging stuff
format="%(filename)s:%(lineno)d - %(levelname)s: %(message)s"
if "BARE_DEBUG" in os.environ.keys():
    logging.basicConfig(level=logging.DEBUG, format=format)
else:
    logging.basicConfig(level=logging.WARNING, format=format)
LOGGER = logging.getLogger(constants.app_name)

class BareNaked():

    config = None
    workdir = None

    def __init__(self):
        self.workdir = tempfile.mkdtemp(prefix=constants.app_name)
        LOGGER.debug("Work directory %s created" % self.workdir)

    def cleanup(self):
        LOGGER.debug("Cleaning up %s" % self.workdir)
        shutil.rmtree(self.workdir)

    def _load_config(self, config_file):
        """
        Loads the properties YAML file
        """

        try:
            LOGGER.debug("Loading %s" % config_file)
            fh = open(config_file)
            self.config = yaml.load(fh)
            fh.close()
            return True
        except Exception, e:
            self.logger.warn(str(e))
            return False

def main():
    # This module should only be imported if called from the cli
    import optparse
    op = optparse.OptionParser(version=constants.app_version)
    op.add_option("-e", "--editor", dest="editor",
                  action="store_true", default=False,
                  help="Start 'editor mode'")
    op.add_option("-p", "--parser", dest="parser",
                  action="store_true", default=False,
                  help="Parse the contents of the source dir")
    op.add_option("-c", "--config", dest="config", default="config.yml",
                  help="Configuration YAML file to use (defaults to config.yml)")
    op.add_option("-o", "--output", dest="output",
                  help="Overrides the output directive from the config file")
    op.add_option("-r", "--rebuild", dest="rebuild", default=False,
                  help="Rebuilds the whole site")
    #parser.add_options("-l", "--plugins")
    (options, args) = op.parse_args()

    bn = None
    try:
        # Validate at least one mode
        if not options.editor and not options.parser:
            raise ValueError("You have to start either in editor or parser mode")

        if options.editor:
            import editor
            bn = editor.Editor()
        if options.parser:
            import parser
            config = os.path.abspath(options.config)
            bn = parser.Parser(config)
        bn.run()
    except Exception, ex:
        LOGGER.error(str(ex))
        if bn:
            bn.cleanup()

if __name__ == "__main__":
    main()

