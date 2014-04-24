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
import os
import re
import sys
import tokenize
from io import StringIO
from token import N_TOKENS

from pies.overrides import *

import _ast
from frosted import reporter as modReporter
from frosted import checker, settings
from frosted.messages import FileSkipped, PythonSyntaxError

__all__ = ['check', 'check_path', 'check_recursive', 'iter_source_code']

_re_noqa = re.compile(r'((frosted)[:=]\s*noqa)|(#\s*noqa)', re.I)


def _noqa_lines(codeString):
    line_nums = []
    g = tokenize.generate_tokens(StringIO(str(codeString)).readline)   # tokenize the string
    for toknum, tokval, begins, _, _ in g:
        lineno = begins[0]
        # not sure what N_TOKENS really means, but in testing, that was what comments were
        # tokenized as
        if toknum == N_TOKENS:
            if _re_noqa.search(tokval):
                line_nums.append(lineno)
    return line_nums


def _should_skip(filename, skip):
    if filename in skip:
        return True

    position = os.path.split(filename)
    while position[1]:
        if position[1] in skip:
            return True
        position = os.path.split(position[0])


def check(codeString, filename, reporter=modReporter.Default, settings_path=None, **setting_overrides):
    """Check the Python source given by codeString for unfrosted flakes."""

    if not settings_path and filename:
        settings_path = os.path.dirname(os.path.abspath(filename))
    settings_path = settings_path or os.getcwd()

    active_settings = settings.from_path(settings_path).copy()
    for key, value in itemsview(setting_overrides):
        access_key = key.replace('not_', '').lower()
        if type(active_settings.get(access_key)) in (list, tuple):
            if key.startswith('not_'):
                active_settings[access_key] = list(set(active_settings[access_key]).difference(value))
            else:
                active_settings[access_key] = list(set(active_settings[access_key]).union(value))
        else:
            active_settings[key] = value
    active_settings.update(setting_overrides)

    if _should_skip(filename, active_settings.get('skip', [])):
        if active_settings.get('directly_being_checked', None) == 1:
            reporter.flake(FileSkipped(filename))
            return 1
        elif active_settings.get('verbose', False):
            ignore = active_settings.get('ignore_frosted_errors', [])
            if(not "W200" in ignore and not "W201" in ignore):
                reporter.flake(FileSkipped(filename, None, verbose=active_settings.get('verbose')))
        return 0

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
            reporter.flake(PythonSyntaxError(filename, msg, lineno, offset, text,
                                             verbose=active_settings.get('verbose')))
        return 1
    except Exception:
        reporter.unexpected_error(filename, 'problem decoding source')
        return 1
    # Okay, it's syntactically valid.  Now check it.
    w = checker.Checker(tree, filename, None, ignore_lines=_noqa_lines(codeString), **active_settings)
    w.messages.sort(key=lambda m: m.lineno)
    for warning in w.messages:
        reporter.flake(warning)
    return len(w.messages)


def check_path(filename, reporter=modReporter.Default, settings_path=None, **setting_overrides):
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
    return check(codestr, filename, reporter, settings_path, **setting_overrides)


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


def check_recursive(paths, reporter=modReporter.Default, settings_path=None, **setting_overrides):
    """Recursively check all source files defined in paths."""
    warnings = 0
    for source_path in iter_source_code(paths):
        warnings += check_path(source_path, reporter, settings_path=None, **setting_overrides)
    return warnings
