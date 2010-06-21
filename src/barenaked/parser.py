#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import logging
import pprint

import barenaked
import constants

LOGGER = logging.getLogger(constants.app_name)

class Parser(barenaked.BareNaked):

    def __init__(self, config_file):
        barenaked.BareNaked.__init__(self, config_file)

    def run(self, output=None):
        if not output and not 'output' in self.config.keys():
            raise UndefinedOutputError('The parser needs an output directory')
        pprint.pprint(self.config)
