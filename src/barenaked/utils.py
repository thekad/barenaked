#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import re
import unicodedata


def slugify(word):
    strip_re = re.compile(r'[^\w\s-]')
    hyphenate_re = re.compile(r'[-\s]+')
    if not isinstance(word, unicode):
        word = unicode(word)
    word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore')
    word = unicode(strip_re.sub('', word).strip().lower())
    return hyphenate_re.sub('-', word)

