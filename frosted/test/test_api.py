"""frosted/test/test_api.py.

Tests all major functionality of the Frosted API

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
OTHER DEALINGS IN THE SOFTWARE.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import tempfile
from io import StringIO

import pytest
from pies.overrides import *

from frosted.api import check_path, check_recursive
from frosted.messages import PythonSyntaxError, UnusedImport
from frosted.reporter import Reporter

from .utils import LoggingReporter, Node


def test_syntax_error():
    """syntax_error reports that there was a syntax error in the source file.

    It reports to the error stream and includes the filename, line number, error message, actual line of source and a
    caret pointing to where the error is

    """
    err = StringIO()
    reporter = Reporter(err, err)
    reporter.flake(PythonSyntaxError('foo.py', 'a problem', 3, 7, 'bad line of source', verbose=True))
    assert ("foo.py:3:7:E402::a problem\n"
            "bad line of source\n"
            "       ^\n") == err.getvalue()


def test_syntax_errorNoOffset():
    """syntax_error doesn't include a caret pointing to the error if offset is passed as None."""
    err = StringIO()
    reporter = Reporter(err, err)
    reporter.flake(PythonSyntaxError('foo.py', 'a problem', 3, None, 'bad line of source', verbose=True))
    assert ("foo.py:3:0:E402::a problem\n"
            "bad line of source\n") == err.getvalue()


def test_multiLineSyntaxError():
    """ If there's a multi-line syntax error, then we only report the last line.

    The offset is adjusted so that it is relative to the start of the last line

    """
    err = StringIO()
    lines = ['bad line of source', 'more bad lines of source']
    reporter = Reporter(err, err)
    reporter.flake(PythonSyntaxError('foo.py', 'a problem', 3, len(lines[0]) + 7, '\n'.join(lines), verbose=True))
    assert ("foo.py:3:6:E402::a problem\n" +
            lines[-1] + "\n" +
            "      ^\n") == err.getvalue()


def test_unexpected_error():
    """unexpected_error reports an error processing a source file."""
    err = StringIO()
    reporter = Reporter(None, err)
    reporter.unexpected_error('source.py', 'error message')
    assert 'source.py: error message\n' == err.getvalue()


def test_flake():
    """flake reports a code warning from Frosted.

    It is exactly the str() of a frosted.messages.Message

    """
    out = StringIO()
    reporter = Reporter(out, None)
    message = UnusedImport('foo.py', Node(42), 'bar')
    reporter.flake(message)
    assert out.getvalue() == "%s\n" % (message,)


def make_temp_file(content):
    """Make a temporary file containing C{content} and return a path to it."""
    _, fpath = tempfile.mkstemp()
    if not hasattr(content, 'decode'):
        content = content.encode('ascii')
    fd = open(fpath, 'wb')
    fd.write(content)
    fd.close()
    return fpath


def assert_contains_output(path, flakeList):
    """Assert that provided causes at minimal the errors provided in the error list."""
    out = StringIO()
    count = check_path(path, Reporter(out, out), verbose=True)
    out_string = out.getvalue()
    assert len(flakeList) >= count
    for flake in flakeList:
        assert flake in out_string


def get_errors(path):
    """Get any warnings or errors reported by frosted for the file at path."""
    log = []
    reporter = LoggingReporter(log)
    count = check_path(path, reporter)
    return count, log


def test_missingTrailingNewline():
    """Source which doesn't end with a newline shouldn't cause any exception to

    be raised nor an error indicator to be returned by check.

    """
    fName = make_temp_file("def foo():\n\tpass\n\t")
    assert_contains_output(fName, [])


def test_check_pathNonExisting():
    """check_path handles non-existing files"""
    count, errors = get_errors('extremo')
    assert count == 1
    assert errors == [('unexpected_error', 'extremo', 'No such file or directory')]


def test_multilineSyntaxError():
    """Source which includes a syntax error which results in the raised SyntaxError.

    text containing multiple lines of source are reported with only
    the last line of that source.

    """
    source = """\
def foo():
    '''

def bar():
    pass

def baz():
    '''quux'''
"""
    # Sanity check - SyntaxError.text should be multiple lines, if it
    # isn't, something this test was unprepared for has happened.
    def evaluate(source):
        exec(source)
    try:
        evaluate(source)
    except SyntaxError:
        e = sys.exc_info()[1]
        assert e.text.count('\n') > 1
    else:
        assert False

    sourcePath = make_temp_file(source)
    assert_contains_output(
        sourcePath,
        ["""\
%s:8:10:E402::invalid syntax
    '''quux'''
          ^
""" % (sourcePath,)])


def test_eofSyntaxError():
    """The error reported for source files which end prematurely causing a
    syntax error reflects the cause for the syntax error.

    """
    sourcePath = make_temp_file("def foo(")
    assert_contains_output(sourcePath, ["""\
%s:1:8:E402::unexpected EOF while parsing
def foo(
        ^
""" % (sourcePath,)])


def test_nonDefaultFollowsDefaultSyntaxError():
    """ Source which has a non-default argument following a default argument

    should include the line number of the syntax error
    However these exceptions do not include an offset

    """
    source = """\
def foo(bar=baz, bax):
    pass
"""
    sourcePath = make_temp_file(source)
    last_line = '       ^\n' if sys.version_info >= (3, 2) else ''
    column = '7:' if sys.version_info >= (3, 2) else '0:'
    assert_contains_output(sourcePath, ["""\
%s:1:%sE402::non-default argument follows default argument
def foo(bar=baz, bax):
%s""" % (sourcePath, column, last_line)])


def test_nonKeywordAfterKeywordSyntaxError():
    """Source which has a non-keyword argument after a keyword argument

    should include the line number of the syntax error
    However these exceptions do not include an offset
    """
    source = """\
foo(bar=baz, bax)
"""
    sourcePath = make_temp_file(source)
    last_line = '            ^\n' if sys.version_info >= (3, 2) else ''
    column = '12:' if sys.version_info >= (3, 2) else '0:'
    assert_contains_output(
        sourcePath,
        ["""\
%s:1:%sE402::non-keyword arg after keyword arg
foo(bar=baz, bax)
%s""" % (sourcePath, column, last_line)])


def test_invalidEscape():
    """The invalid escape syntax raises ValueError in Python 2."""
    sourcePath = make_temp_file(r"foo = '\xyz'")
    if PY2:
        decoding_error = "%s: problem decoding source\n" % (sourcePath,)
    else:
        decoding_error = "(unicode error) 'unicodeescape' codec can't decode bytes"
    assert_contains_output(sourcePath, (decoding_error, ))


def test_permissionDenied():
    """If the source file is not readable, this is reported on standard error."""
    sourcePath = make_temp_file('')
    os.chmod(sourcePath, 0)
    count, errors = get_errors(sourcePath)
    assert count == 1
    assert errors == [('unexpected_error', sourcePath, "Permission denied")]


def test_frostedWarning():
    """If the source file has a frosted warning, this is reported as a 'flake'."""
    sourcePath = make_temp_file("import foo")
    count, errors = get_errors(sourcePath)
    assert count == 1
    assert errors == [('flake', str(UnusedImport(sourcePath, Node(1), 'foo')))]


@pytest.mark.skipif("PY3")
def test_misencodedFileUTF8():
    """If a source file contains bytes which cannot be decoded, this is reported on stderr."""
    SNOWMAN = chr(0x2603)
    source = ("""\
# coding: ascii
x = "%s"
""" % SNOWMAN).encode('utf-8')
    sourcePath = make_temp_file(source)
    assert_contains_output(sourcePath, ["%s: problem decoding source\n" % (sourcePath, )])


def test_misencodedFileUTF16():
    """If a source file contains bytes which cannot be decoded, this is reported on stderr."""
    SNOWMAN = chr(0x2603)
    source = ("""\
# coding: ascii
x = "%s"
""" % SNOWMAN).encode('utf-16')
    sourcePath = make_temp_file(source)
    assert_contains_output(sourcePath, ["%s: problem decoding source\n" % (sourcePath,)])


def test_check_recursive():
    """check_recursive descends into each directory, finding Python files and reporting problems."""
    tempdir = tempfile.mkdtemp()
    os.mkdir(os.path.join(tempdir, 'foo'))
    file1 = os.path.join(tempdir, 'foo', 'bar.py')
    fd = open(file1, 'wb')
    fd.write("import baz\n".encode('ascii'))
    fd.close()
    file2 = os.path.join(tempdir, 'baz.py')
    fd = open(file2, 'wb')
    fd.write("import contraband".encode('ascii'))
    fd.close()
    log = []
    reporter = LoggingReporter(log)
    warnings = check_recursive([tempdir], reporter)
    assert warnings == 2
    assert sorted(log) == sorted([('flake', str(UnusedImport(file1, Node(1), 'baz'))),
                                  ('flake', str(UnusedImport(file2, Node(1), 'contraband')))])
