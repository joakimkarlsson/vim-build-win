#!/usr/bin/env python
import subprocess as sp
import argparse as ap
import os.path as op
import shutil
import glob
import sys
import os


def main():
    args = _parse_args()

    ensure_mercurial()
    ensure_source_available()
    pull_source_if(args.pull)

    env = visual_studio_environment()
    add_python_path_to(env)
    add_python_build_config_to(env)

    clean(env)
    build(env)

    if args.gvim:
        add_gui_to_build_env(env)
        clean(env)
        build(env)

    ensure_bin_dir()
    copy_binaries()


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


def copy_binaries():
    print('Copying runtime files...')
    shutil.copytree(runtime_dir(), bin_dir())
    for f in binaries():
        print('Copying {}...'.format(f))
        shutil.copy(f, bin_dir())


def binaries():
    return (glob.glob(op.join(vim_src_dir(), '**/*.exe')) +
            glob.glob(op.join(vim_src_dir(), '*.exe')) +
            glob.glob(op.join(vim_src_dir(), '**/*.dll')) +
            glob.glob(op.join(vim_src_dir(), '*.dll')))




def visual_studio_environment():
    res = sp.check_output(['cmd', '/c', 'vsvarshelper.bat'],
                          cwd=script_dir())
    res = res.decode('utf-8')

    return dict(line.split('=') for line in res.split('\r\n') if '=' in line)

def add_python_build_config_to(env):
    env['CPUNR'] = 'i686'
    env['CPU'] = 'AMD64'
    env['FEATURES'] = 'huge'
    env['FARSI'] = 'no'
    env['ARABIC'] = 'no'
    env['DYNAMIC_PYTHON3'] = 'yes'
    env['PYTHON3'] = r'C:\Python34'
    env['PYTHON3_VER'] = '34'


def add_gui_to_build_env(env):
    env['GUI'] = 'yes'
    env['DIRECTX'] = 'yes'


def add_python_path_to(env):
    env['PATH'] = r'C:\Python34;' + env['PATH']


def build(env):
    print('Building vim...')
    sp.check_call(['cmd', '/c', nmake(), '-f', 'Make_mvc.mak', 'CPU=AMD64'], env=env, cwd=vim_src_dir())


def clean(env):
    print('Cleaning up build...')
    sp.check_call(['cmd', '/c', nmake(), '-f', 'Make_mvc.mak', 'clean'], env=env, cwd=vim_src_dir())


def nmake():
    return op.join(vc_bin_dir(), 'nmake')

def vc_bin_dir():
    return op.expandvars(op.join(
        '%PROGRAMFILES(X86)%', 'Microsoft Visual Studio 10.0', 'VC', 'bin'))


def hg_clone():
    sp.check_call(['hg', 'clone', 'https://vim.googlecode.com/hg/', vim_dir()])


def hg_pull():
    sp.check_call(['hg', 'pull'], cwd=vim_dir())
    sp.check_call(['hg', 'update'], cwd=vim_dir())


def vim_source_available():
    return op.isdir(vim_dir())


def ensure_bin_dir():
    print('Ensuring bin dir is available...')
    if op.isdir(bin_dir()):
        print('Removing old bin dir...')
        shutil.rmtree(bin_dir())


def bin_dir():
    return op.join(script_dir(), 'bin')

def runtime_dir():
    return op.join(vim_dir(), 'runtime')


def vim_src_dir():
    return op.join(vim_dir(), 'src')


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

    p.add_argument('--gvim', '-g', action='store_true', default=True,
                   help='Build gvim as well')

    return p.parse_args()

if __name__ == '__main__':
    sys.exit(main())
