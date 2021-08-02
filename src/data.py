#!/usr/bin/env python3
'''
Load data files from the game's "data" directory.
'''
# TODO: Add caching.

import os, sys

base_dir = os.path.dirname(sys.executable if hasattr(sys, "frozen") else sys.argv[0])

data_dir = os.path.normpath(os.path.join(base_dir, 'data'))

if not os.path.isdir(data_dir):
    try_base_dir = os.path.dirname(os.path.abspath(base_dir))
    try_data_dir = os.path.join(try_base_dir, 'data')
    if os.path.isdir(try_data_dir):
        base_dir = try_base_dir
        data_dir = try_data_dir
        print("* The data dir was detected as \"{}\"".format(data_dir))
    else:
        print("Error: data dir was not found in base_dir \"{}\""
              " nor its parent directory.".format(base_dir))

def get_data_dir():
    return data_dir

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    path = os.path.join(data_dir, filename)
    #if not os.path.isfile(path):
    return path

def basepath(filename):
    '''Determine the path to a file in the base directory.
    '''
    return os.path.join(base_dir, filename)

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

