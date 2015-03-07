#!/usr/bin/env python
import subprocess as sp
import argparse as ap
import os.path as op
import shutil
import sys
import os


def main():
    args = _parse_args()

    ensure_mercurial()
    ensure_source_available()
    pull_source_if(args.pull)


def ensure_mercurial():
    if not shutil.which('hg'):
        raise Exception('Mercurial is not found. Please install it')

def ensure_source_available():
    print('Making sure source directories are available...')
    if not op.isdir(build_dir()):
        os.makedirs(build_dir())

    if not op.isdir(vim_dir()):
        print('No vim source dir found, cloning it...')
        hg_clone()


def pull_source_if(should_pull):
    if not should_pull:
        return

    print('Retrieving source from vim repo...')
    hg_pull()


def hg_clone():
    sp.check_call(['hg', 'clone', 'https://vim.googlecode.com/hg/', vim_dir()])


def hg_pull():
    sp.check_call(['hg', 'pull'], cwd=vim_dir())
    sp.check_call(['hg', 'update'], cwd=vim_dir())


def vim_source_available():
    return op.isdir(vim_dir())


def vim_dir():
    return op.join(build_dir(), 'vim')


def build_dir():
    return op.join(script_dir(), 'build')


def script_dir():
    return op.abspath(op.dirname(__file__))


def _parse_args():
    p = ap.ArgumentParser(description="Builds vim and gvim")

    p.add_argument('--pull', '-p', action='store_true', default=False,
                   help='pull the latest changes from the vim repo')

    return p.parse_args()

if __name__ == '__main__':
    sys.exit(main())
