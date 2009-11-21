#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import logging
import subprocess

import constants
import barenaked

LOGGER = logging.getLogger(constants.app_name)

META_TMPL = """
---
# -*- mode: python; sh-basic-offset: 2; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=2 softtabstop=2 expandtab shiftwidth=2 fileencoding=utf-8

title:
# Specify date if you don't want the file's mtime
# to be used (i.e. if this post is in the future)
# Date must be in rfc2822, i.e. date -R (TZ is ignored)
#date:
# Author username must exist in the global config file to be parsed
author:
# If you want to override your global comment settings, say Yes or No
#comments:
# You can specify a list of tags here
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
        if editor:
            files = "%(wd)s/meta.yaml %(wd)s/body.txt" % ({"wd": self.workdir})
            subprocess.Popen()
