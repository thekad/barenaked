#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import logging
import os
import sys
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
        pass

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

    # Validate at least one mode
    if not options.editor and not options.parser:
        raise ValueError("You have to start either in editor or parser mode")

    if options.editor:
        import editor
        e = editor.Editor()
        e.run()

    if options.parser:
        import parser
        config = os.path.abspath(options.config)
        p = parser.Parser(config)
        p.run()

if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        LOGGER.error(e)
