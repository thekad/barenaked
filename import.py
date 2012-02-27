#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import argparse
import codecs
import git
import json
import logging
import os
import re
import sys
import unicodedata
import yaml


format = '%(filename)s:%(lineno)d - %(levelname)s: %(message)s'
if 'BARE_DEBUG' in os.environ.keys():
    logging.basicConfig(level=logging.DEBUG, format=format)
else:
    logging.basicConfig(level=logging.INFO, format=format)

LOGGER = logging.getLogger(__file__)
STRIP_RE = re.compile(r'[^\w\s-]')
HYPHENATE_RE = re.compile(r'[-\s]+')


def slugify(word):
    "Save the file as a sanitized slug for web links"

    if not isinstance(word, unicode):
        word = unicode(word)
    word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore')
    word = unicode(STRIP_RE.sub('', word).strip().lower())
    return HYPHENATE_RE.sub('-', word)


def write_file(output, prefix, post):
    "Write the contents to a given directory"

    slug = slugify(post['title'])
    path = os.path.join(output, prefix, '%s.markdown' % (slug, ))
    f = codecs.open(path, 'wb', encoding='utf-8')
    LOGGER.debug('Writing %s' % (path, ))
    f.write(post['body'])
#   I hate files with no \n at EOF
    f.write('\n')
    f.close()
    return path


def commit(index, fpath, post):
    "Commit the given file to the git repository"

    commit_msg = '%(title)s\n' % post
    commit_msg = '%s\n%s\n' % (commit_msg, json.dumps({
        'tags': post['tags'],
        'createtime': unicode(post['createtime']),
    }, indent=4))
    index.add([fpath])
    return index.commit(commit_msg.encode(encoding='utf-8'))


def main(input, output, prefix='posts'):
    "Main routine"

    fh = codecs.open(input, 'rb', encoding='utf-8')
    posts = yaml.load(fh.read())
    fh.close()
    LOGGER.info('Found %d posts' % (len(posts)))
    LOGGER.info('Opening git repository at %s' % (output))
    try:
        repo = git.Repo(output)
    except git.exc.NoSuchPathError as nspe:
        os.makedirs(output)
        repo = git.Repo.init(output)
    index = repo.index
    if not os.path.isdir(os.path.join(output, prefix)):
        os.makedirs(os.path.join(output, prefix))
    for idx, post in posts.items():
        fpath = write_file(output, prefix, post)
        git_sha = commit(index, fpath, post)
        LOGGER.debug('Committed new git sha %s' % (git_sha, ))
    LOGGER.info('Done.')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('-i', '--input', help='YAML Input File', required=True)
    ap.add_argument('-o', '--output', help='Output git directory',
        required=True)
    ap.add_argument('-p', '--prefix', help='Directory prefix inside the '
        'git directory', default='posts')
    args = ap.parse_args()
    sys.exit(main(input=args.input, output=os.path.expanduser(args.output),
        prefix=args.prefix))

