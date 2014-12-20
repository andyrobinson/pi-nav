import sys, os

def setup_test():
    testdir = os.path.dirname(__file__)
    srcdir = '../src'
    sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
    sys.path.insert(0, os.path.abspath(os.path.join(testdir, 'utils')))