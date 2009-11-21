#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import logging

import constants
import barenaked

LOGGER = logging.getLogger(constants.app_name)

META_TMPL = """
---
# -*- coding: utf-8 -*-
# vim: ai ts=2 sts=2 et sw=2

title:
# Specify date if you don't want the file mtime
# to be used (i.e. this post is in the future)
# Date must be in rfc2822, i.e. date -R (TZ is ignored)
#date:
author:
# If you want to override your global comment settings, say Yes or No
#comments:
tags:
  - general
"""

class Editor(barenaked.BareNaked):

    editor = None

    def __init__(self, config_file=None):
        barenaked.BareNaked.__init__(self)

    def set_editor(self, editor=None):
        if editor:
            self.editor = editor
            return
        if "EDITOR" in os.environ.keys():
            self.editor = os.environ["EDITOR"]
            return
    def run(self):
        print "Here"
