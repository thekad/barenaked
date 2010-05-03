#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

class ConfigNotFoundError(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return self.parameter

class UndefinedOutputError(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return self.parameter

class InvalidEditorError(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return self.parameter

