import os
import sys
import unittest

if __name__ == "__main__":
    directory = os.path.dirname(os.path.realpath(__file__))
    suite = unittest.TestLoader().discover(directory)

    args = sys.argv[1:]
    if args:
        tests = ['tests.' + test for test in args]
        suite = unittest.TestLoader().loadTestsFromNames(tests)

    unittest.TextTestRunner().run(suite)
