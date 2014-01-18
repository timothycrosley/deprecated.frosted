"""frosted/api.py.

Defines the api for the command-line frosted utility

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
from optparse import OptionParser

from pies.overrides import *

import _ast
from frosted import reporter as modReporter
from frosted import __version__, checker

__all__ = ['check', 'check_path', 'check_recursive', 'iter_source_code', 'main']


def check(codeString, filename, reporter=modReporter.Default):
    """Check the Python source given by codeString for unfrosted flakes."""
    # First, compile into an AST and handle syntax errors.
    try:
        tree = compile(codeString, filename, "exec", _ast.PyCF_ONLY_AST)
    except SyntaxError:
        value = sys.exc_info()[1]
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            reporter.unexpected_error(filename, 'problem decoding source')
        else:
            reporter.syntax_error(filename, msg, lineno, offset, text)
        return 1
    except Exception:
        reporter.unexpected_error(filename, 'problem decoding source')
        return 1
    # Okay, it's syntactically valid.  Now check it.
    w = checker.Checker(tree, filename)
    w.messages.sort(key=lambda m: m.lineno)
    for warning in w.messages:
        reporter.flake(warning)
    return len(w.messages)


def check_path(filename, reporter=modReporter.Default):
    """Check the given path, printing out any warnings detected."""
    try:
        with open(filename, 'U') as f:
            codestr = f.read() + '\n'
    except UnicodeError:
        reporter.unexpected_error(filename, 'problem decoding source')
        return 1
    except IOError:
        msg = sys.exc_info()[1]
        reporter.unexpected_error(filename, msg.args[1])
        return 1
    return check(codestr, filename, reporter)


def iter_source_code(paths):
    """Iterate over all Python source files defined in paths."""
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.py'):
                        yield os.path.join(dirpath, filename)
        else:
            yield path


def check_recursive(paths, reporter=modReporter.Default):
    """Recursively check all source files defined in paths."""
    warnings = 0
    for sourcePath in iter_source_code(paths):
        warnings += check_path(sourcePath, reporter)
    return warnings


def main(prog=None):
    parser = OptionParser(prog=prog, version=__version__)
    __, args = parser.parse_args()
    if args:
        warnings = check_recursive(args)
    else:
        warnings = check(sys.stdin.read(), '<stdin>')
    raise SystemExit(warnings > 0)
