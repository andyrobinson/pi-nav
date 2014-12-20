import sys, os

def setup_test():
    testdir = os.path.dirname(__file__)
    sys.path.insert(0, os.path.abspath(os.path.join(testdir, '../src')))
    sys.path.insert(0, os.path.abspath(os.path.join(testdir, '../test/utils')))