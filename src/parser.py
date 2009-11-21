#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import logging
import pprint

import constants
import barenaked

LOGGER = logging.getLogger(constants.app_name)

class Parser(barenaked.BareNaked):

    def __init__(self, config_file):
        barenaked.BareNaked.__init__(self)
        if not self._load_config(config_file):
            raise ConfigNotFoundError("Config file '%s' was not found or is invalid" % config_file)

    def run(self, output=None):
        LOGGER.debug("tst")
        if not output and not "output" in self.config.keys():
            raise UndefinedOutputError("The parser needs an output directory")
        pprint.pprint(self.config)
