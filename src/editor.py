#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import barenaked

class BareNakedEditor(barenaked.BareNaked):

    editor = None

    def __init__(self, config_file=None):
        BareNaked.__init__(self)

    def set_editor(self, editor=None):
        if editor:
            self.editor = editor
            return
        if "EDITOR" in os.environ.keys():
            self.editor = os.environ["EDITOR"]
            return

