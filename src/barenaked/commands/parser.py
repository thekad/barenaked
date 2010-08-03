#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import logging
import pprint
import re
import unicodedata

from barenaked import base
from barenaked import constants

LOGGER = logging.getLogger(constants.app_name)

class Parser(base.BareNaked):

    def __init__(self, config_file):
        base.BareNaked.__init__(self, config_file)

    def run(self, output=None):
        if not output and not 'output' in self.config.keys():
            raise UndefinedOutputError('The parser needs an output directory')
        pprint.pprint(self.config)

    def _build_url(self, title):
        return "%s/%d/%d/%d/%s" % (self.config['url'],
            today.year, today.month, today.day,
            self._slugify(title))

    def _slugify(self, title):
        strip_re = re.compile(r'[^\w\s-]')
        hyphenate_re = re.compile(r'[-\s]+')
        if not isinstance(title, unicode):
            title = unicode(title)
        title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
        title = unicode(strip_re.sub('', title).strip().lower())
        return hyphenate_re.sub('-', title)

    def load_post(self):
        f = os.path.join(self.workdir, 'meta.yaml')
        meta = open(f, 'rb')
        meta.close()
        f = os.path.join(self.workdir, 'body.txt')
        LOGGER.debug('Writing file %s' % f)
        body = open(f, 'wb')
        body.close()

