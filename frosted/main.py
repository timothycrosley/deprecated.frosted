#!/usr/bin/env python
""" Implementation of the command-line frosted tool.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import sys

from pies.overrides import *

from frosted import __version__
from frosted.api import check, check_path, check_recursive


def main():
    warnings = 0

    parser = argparse.ArgumentParser(description='Quickly check the correctness of your Python scripts.')
    parser.add_argument('files', nargs='+', help='One file or a list of Python source files to check the syntax of.')
    parser.add_argument('-r', '--recursive', dest='recursive', action='store_true',
                        help='Recursively look for Python files to check')
    parser.add_argument('-s', '--skip', help='Files that frosted should skip over.', dest='skip', action='append')
    parser.add_argument('-d', '--with-doctests', help='Run frosted against doctests', dest='run_doctests',
                        action='store_true')
    parser.add_argument('-i', '--ignore', help='Specify error codes that should be ignored.',
                        dest='ignore_frosted_errors', action='append')
    parser.add_argument('-di', '--dont-ignore', help='Specify error codes that should not be ignored in any case.',
                        dest='not_ignore_frosted_errors', action='append')
    parser.add_argument('-vb', '--verbose', help='Explicitly separate each section of data when displaying errors.',
                        dest='verbose', action='store_true')
    parser.add_argument('-v', '--version', action='version', version='frosted {0}'.format(__version__))
    arguments = dict((key, value) for (key, value) in itemsview(vars(parser.parse_args())) if value)
    file_names = arguments.pop('files', [])
    if file_names == ['-']:
        check(sys.stdin.read(), '<stdin>', **arguments)
    elif arguments.get('recursive'):
        warnings = check_recursive(file_names, **arguments)
    else:
        warnings = 0
        for file_path in file_names:
            try:
                warnings += check_path(file_path, directly_being_checked=len(file_names), **arguments)
            except IOError as e:
                print("WARNING: Unable to parse file {0} due to {1}".format(file_name, e))

    raise SystemExit(warnings > 0)


if __name__ == "__main__":
    main()
