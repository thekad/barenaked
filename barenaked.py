#!/usr/bin/env python
#
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import bottle
import git
try:
    import simplejson as json
except ImportError:
    import json
import os
import sys

CONF = {
    'host': 'localhost',
    'port': 8668,
    'reload': True,
    'branch': 'master',
    'memcached': ['localhost:11211',],
    'repo': None,
}

cfg_file = os.environ.get('BARERC', '~/.barerc')
cfg_file = os.path.realpath(os.path.expanduser(cfg_file))
if os.path.isfile(cfg_file):
    cfg_file = open(os.path.realpath(os.path.expanduser(cfg_file)), 'rb')
    conf = json.load(cfg_file)
    cfg_file.close()
    for k, v in conf.items():
        CONF[k] = v

bare = bottle.Bottle()

@bare.route('/')
@bare.route('/HEAD')
def head():
    """Returns the tip of the configured head in git"""

    return 'Holla!'

bottle.run(bare, host=CONF['host'], port=CONF['port'], reloader=CONF['reload'])

