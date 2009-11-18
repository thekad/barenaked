#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import logging
import os
import pprint
import sys
import yaml

# Constants
__app__ = "BareNaked"
__version__ = "0.1"
__author__ = "Jorge A Gallegos <kad@blegh.net>"

# Logging
logging.basicConfig(format="%(filename)s:%(lineno)d - "
                    "%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__app__)
LOGGER.setLevel(logging.WARNING)

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
            fh = open(config_file)
            self.config = yaml.load(fh)
            fh.close()
            return True
        except Exception, e:
            LOGGER.warn(str(e))
            return False

def main():
    # This module should only be imported if called from the cli
    import optparse
    parser = optparse.OptionParser(version=__version__)
    parser.add_option("-e", "--editor", dest="editor",
                      action="store_true", default=False,
                      help="Start 'editor mode'")
    parser.add_option("-p", "--parser", dest="parser",
                      action="store_true", default=False,
                      help="Parse the contents of the base dir")
    parser.add_option("-c", "--config", dest="config", default="config.yml",
                      help="Configuration YAML file to use (defaults to config.yml)")
    parser.add_option("-o", "--output", dest="output",
                      help="Overrides the output directive from the config file")
    parser.add_option("-r", "--rebuild", dest="rebuild", default=False,
                      help="Rebuilds the whole site")
    #parser.add_options("-l", "--plugins")
    (options, args) = parser.parse_args()
    # Validate at least one mode
    if not options.editor and not options.parser:
        raise ValueError("You have to start either in editor or parser mode")

    if options.editor:
        editor = BareNakedEditor()
        editor.run()

    if options.parser:
        config = os.path.abspath(options.config)
        parser = BareNakedParser(config)
        parser.run()

if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        LOGGER.error(e)
        sys.exit(1)
