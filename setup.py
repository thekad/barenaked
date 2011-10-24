#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Bare Naked Blog
# Copyright 2009, Jorge A Gallegos <kad@blegh.net>

import setuptools
from src.barenaked import constants

setuptools.setup (
    name = constants.app_name,
    version = constants.app_version,
    package_dir = { '': 'src' },
    packages = setuptools.find_packages('src'),
    zip_safe = False,
    install_requires = [
        'jinja2>=2.2.0',
        'Markdown2',
        'PyYAML>=3.09',
        'argparse',
        'PyRSS2Gen',
    ],
    entry_points = {
        'console_scripts': [
            'barenaked = barenaked.base:main',
        ],
    },
    author = constants.author,
    author_email = constants.author_email,
    maintainer = constants.author,
    maintainer_email = constants.author_email,
    description = constants.app_desc,
    license = 'MIT',
    keywords = 'blog html',
    url = 'http://github.com/thekad/barenaked',
)
