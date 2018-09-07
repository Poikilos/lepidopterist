'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os, sys

base_dir = os.path.dirname(sys.executable if hasattr(sys, "frozen") else sys.argv[0])
data_dir = os.path.normpath(os.path.join(base_dir, 'data'))

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    return os.path.join(data_dir, filename)

def basepath(filename):
    '''Determine the path to a file in the base directory.
    '''
    return os.path.join(base_dir, filename)

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

