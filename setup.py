#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

from setuptools import setup

setup(
    name='barenaked',
    packages=[
        'barenaked',
    ],
    version='0.3',
    url='http://github.com/thekad/barenaked/',
    description='A bare-naked approach to blogging.',
    author='Jorge Gallegos',
    author_email='kad@blegh.net',
    license='WTFPL',
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    'install_requires': [
        'distribute',
        'bottle==0.11.6',
        'feedgenerator==1.7',
        'GitPython==0.3.2.RC1',
        'python-memcached==1.53',
        'PyYAML==3.10',
    ]
)
