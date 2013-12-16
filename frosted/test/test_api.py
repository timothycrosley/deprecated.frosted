"""
    frosted/test/test_api.py

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
import shutil
import subprocess
import sys
import tempfile
from collections import namedtuple
from io import StringIO

from frosted.api import check_path, check_recursive, iter_source_code
from frosted.messages import UnusedImport
from frosted.reporter import Reporter
from frosted.test.harness import TestCase
from pies.overrides import *
from pies.unittest import skipIf


class Node(namedtuple('Node', ['lineno', 'col_offset'])):
    """
        A mock AST Node.
    """

    def __new__(cls, lineno, col_offset=0):
        return super(Node, cls).__new__(cls, lineno, col_offset)


class LoggingReporter(namedtuple('LoggingReporter', ['log'])):
    """
        A mock Reporter implementation.
    """

    def flake(self, message):
        self.log.append(('flake', str(message)))

    def unexpected_error(self, filename, message):
        self.log.append(('unexpected_error', filename, message))

    def syntax_error(self, filename, msg, lineno, offset, line):
        self.log.append(('syntax_error', filename, msg, lineno, offset, line))


class TestIterSourceCode(TestCase):
    """
    Tests for L{iter_source_code}.
    """

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def makeEmptyFile(self, *parts):
        assert parts
        fpath = os.path.join(self.tempdir, *parts)
        fd = open(fpath, 'a')
        fd.close()
        return fpath

    def test_emptyDirectory(self):
        """
        There are no Python files in an empty directory.
        """
        self.assertEqual(list(iter_source_code([self.tempdir])), [])

    def test_singleFile(self):
        """
        If the directory contains one Python file, C{iter_source_code} will find
        it.
        """
        childpath = self.makeEmptyFile('foo.py')
        self.assertEqual(list(iter_source_code([self.tempdir])), [childpath])

    def test_onlyPythonSource(self):
        """
        Files that are not Python source files are not included.
        """
        self.makeEmptyFile('foo.pyc')
        self.assertEqual(list(iter_source_code([self.tempdir])), [])

    def test_recurses(self):
        """
        If the Python files are hidden deep down in child directories, we will
        find them.
        """
        os.mkdir(os.path.join(self.tempdir, 'foo'))
        apath = self.makeEmptyFile('foo', 'a.py')
        os.mkdir(os.path.join(self.tempdir, 'bar'))
        bpath = self.makeEmptyFile('bar', 'b.py')
        cpath = self.makeEmptyFile('c.py')
        self.assertEqual(
            sorted(iter_source_code([self.tempdir])),
            sorted([apath, bpath, cpath]))

    def test_multipleDirectories(self):
        """
        L{iter_source_code} can be given multiple directories.  It will recurse
        into each of them.
        """
        foopath = os.path.join(self.tempdir, 'foo')
        barpath = os.path.join(self.tempdir, 'bar')
        os.mkdir(foopath)
        apath = self.makeEmptyFile('foo', 'a.py')
        os.mkdir(barpath)
        bpath = self.makeEmptyFile('bar', 'b.py')
        self.assertEqual(
            sorted(iter_source_code([foopath, barpath])),
            sorted([apath, bpath]))

    def test_explicitFiles(self):
        """
        If one of the paths given to L{iter_source_code} is not a directory but
        a file, it will include that in its output.
        """
        epath = self.makeEmptyFile('e.py')
        self.assertEqual(list(iter_source_code([epath])),
                         [epath])


class TestReporter(TestCase):
    """
    Tests for L{Reporter}.
    """

    def test_syntax_error(self):
        """
        C{syntax_error} reports that there was a syntax error in the source
        file.  It reports to the error stream and includes the filename, line
        number, error message, actual line of source and a caret pointing to
        where the error is.
        """
        err = StringIO()
        reporter = Reporter(None, err)
        reporter.syntax_error('foo.py', 'a problem', 3, 7, 'bad line of source')
        self.assertEqual(
            ("foo.py:3:7: a problem\n"
             "bad line of source\n"
             "       ^\n"),
            err.getvalue())

    def test_syntax_errorNoOffset(self):
        """
        C{syntax_error} doesn't include a caret pointing to the error if
        C{offset} is passed as C{None}.
        """
        err = StringIO()
        reporter = Reporter(None, err)
        reporter.syntax_error('foo.py', 'a problem', 3, None,
                             'bad line of source')
        self.assertEqual(
            ("foo.py:3: a problem\n"
             "bad line of source\n"),
            err.getvalue())

    def test_multiLineSyntaxError(self):
        """
        If there's a multi-line syntax error, then we only report the last
        line.  The offset is adjusted so that it is relative to the start of
        the last line.
        """
        err = StringIO()
        lines = [
            'bad line of source',
            'more bad lines of source',
        ]
        reporter = Reporter(None, err)
        reporter.syntax_error('foo.py', 'a problem', 3, len(lines[0]) + 7,
                             '\n'.join(lines))
        self.assertEqual(
            ("foo.py:3:6: a problem\n" +
             lines[-1] + "\n" +
             "      ^\n"),
            err.getvalue())

    def test_unexpected_error(self):
        """
        C{unexpected_error} reports an error processing a source file.
        """
        err = StringIO()
        reporter = Reporter(None, err)
        reporter.unexpected_error('source.py', 'error message')
        self.assertEqual('source.py: error message\n', err.getvalue())

    def test_flake(self):
        """
        C{flake} reports a code warning from Frosted.  It is exactly the
        str() of a L{frosted.messages.Message}.
        """
        out = StringIO()
        reporter = Reporter(out, None)
        message = UnusedImport('foo.py', Node(42), 'bar')
        reporter.flake(message)
        self.assertEqual(out.getvalue(), "%s\n" % (message,))


class CheckTests(TestCase):
    """
    Tests for L{check} and L{chefackPath} which check a file for flakes.
    """

    def makeTempFile(self, content):
        """
        Make a temporary file containing C{content} and return a path to it.
        """
        _, fpath = tempfile.mkstemp()
        if not hasattr(content, 'decode'):
            content = content.encode('ascii')
        fd = open(fpath, 'wb')
        fd.write(content)
        fd.close()
        return fpath

    def assert_contains_errors(self, path, errorList):
        """
            Assert that provided causes at minimal the errors provided in the error list.
        """
        error = StringIO()
        (outer, sys.stderr) = (sys.stderr, error)
        try:
            count = check_path(path)
        finally:
            sys.stderr = outer

        error_string = error.getvalue()
        self.assertTrue((errorList) >= count)
        for error in errorList:
            self.assertTrue(error in error_string)

    def getErrors(self, path):
        """
        Get any warnings or errors reported by frosted for the file at C{path}.

        @param path: The path to a Python file on disk that frosted will check.
        @return: C{(count, log)}, where C{count} is the number of warnings or
            errors generated, and log is a list of those warnings, presented
            as structured data.  See L{LoggingReporter} for more details.
        """
        log = []
        reporter = LoggingReporter(log)
        count = check_path(path, reporter)
        return count, log

    def test_legacyScript(self):
        from frosted.scripts import frosted as script_frosted
        self.assertIs(script_frosted.check_path, check_path)

    def test_missingTrailingNewline(self):
        """
        Source which doesn't end with a newline shouldn't cause any
        exception to be raised nor an error indicator to be returned by
        L{check}.
        """
        fName = self.makeTempFile("def foo():\n\tpass\n\t")
        self.assert_contains_errors(fName, [])

    def test_check_pathNonExisting(self):
        """
        L{check_path} handles non-existing files.
        """
        count, errors = self.getErrors('extremo')
        self.assertEqual(count, 1)
        self.assertEqual(
            errors,
            [('unexpected_error', 'extremo', 'No such file or directory')])

    def test_multilineSyntaxError(self):
        """
        Source which includes a syntax error which results in the raised
        L{SyntaxError.text} containing multiple lines of source are reported
        with only the last line of that source.
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
            self.assertTrue(e.text.count('\n') > 1)
        else:
            self.fail()

        sourcePath = self.makeTempFile(source)
        self.assert_contains_errors(
            sourcePath,
            ["""\
%s:8:10: invalid syntax
    '''quux'''
          ^
""" % (sourcePath,)])

    def test_eofSyntaxError(self):
        """
        The error reported for source files which end prematurely causing a
        syntax error reflects the cause for the syntax error.
        """
        sourcePath = self.makeTempFile("def foo(")
        self.assert_contains_errors(
            sourcePath,
            ["""\
%s:1:8: unexpected EOF while parsing
def foo(
        ^
""" % (sourcePath,)])

    def test_nonDefaultFollowsDefaultSyntaxError(self):
        """
        Source which has a non-default argument following a default argument
        should include the line number of the syntax error.  However these
        exceptions do not include an offset.
        """
        source = """\
def foo(bar=baz, bax):
    pass
"""
        sourcePath = self.makeTempFile(source)
        last_line = '       ^\n' if sys.version_info >= (3, 2) else ''
        column = '7:' if sys.version_info >= (3, 2) else ''
        self.assert_contains_errors(
            sourcePath,
            ["""\
%s:1:%s non-default argument follows default argument
def foo(bar=baz, bax):
%s""" % (sourcePath, column, last_line)])

    def test_nonKeywordAfterKeywordSyntaxError(self):
        """
        Source which has a non-keyword argument after a keyword argument should
        include the line number of the syntax error.  However these exceptions
        do not include an offset.
        """
        source = """\
foo(bar=baz, bax)
"""
        sourcePath = self.makeTempFile(source)
        last_line = '            ^\n' if sys.version_info >= (3, 2) else ''
        column = '12:' if sys.version_info >= (3, 2) else ''
        self.assert_contains_errors(
            sourcePath,
            ["""\
%s:1:%s non-keyword arg after keyword arg
foo(bar=baz, bax)
%s""" % (sourcePath, column, last_line)])

    def test_invalidEscape(self):
        """
        The invalid escape syntax raises ValueError in Python 2
        """
        # ValueError: invalid \x escape
        ver = sys.version_info
        sourcePath = self.makeTempFile(r"foo = '\xyz'")
        last_line = '       ^\n' if ver >= (3, 2) else ''
        # Column has been "fixed" since 3.2.4 and 3.3.1
        col = 1 if ver >= (3, 3, 1) or ((3, 2, 4) <= ver < (3, 3)) else 2
        self.assert_contains_errors(sourcePath, ("(unicode error) 'unicodeescape' codec can't decode bytes",))

    def test_permissionDenied(self):
        """
        If the source file is not readable, this is reported on standard
        error.
        """
        sourcePath = self.makeTempFile('')
        os.chmod(sourcePath, 0)
        count, errors = self.getErrors(sourcePath)
        self.assertEqual(count, 1)
        self.assertEqual(
            errors,
            [('unexpected_error', sourcePath, "Permission denied")])

    def test_frostedWarning(self):
        """
        If the source file has a frosted warning, this is reported as a
        'flake'.
        """
        sourcePath = self.makeTempFile("import foo")
        count, errors = self.getErrors(sourcePath)
        self.assertEqual(count, 1)
        self.assertEqual(
            errors, [('flake', str(UnusedImport(sourcePath, Node(1), 'foo')))])

    @skipIf(sys.version_info >= (3,), "not relevant")
    def test_misencodedFileUTF8(self):
        """
        If a source file contains bytes which cannot be decoded, this is
        reported on stderr.
        """
        SNOWMAN = chr(0x2603)
        source = ("""\
# coding: ascii
x = "%s"
""" % SNOWMAN).encode('utf-8')
        sourcePath = self.makeTempFile(source)
        self.assert_contains_errors(
            sourcePath, ["%s: problem decoding source\n" % (sourcePath,)])

    def test_misencodedFileUTF16(self):
        """
        If a source file contains bytes which cannot be decoded, this is
        reported on stderr.
        """
        SNOWMAN = chr(0x2603)
        source = ("""\
# coding: ascii
x = "%s"
""" % SNOWMAN).encode('utf-16')
        sourcePath = self.makeTempFile(source)
        self.assert_contains_errors(
            sourcePath, ["%s: problem decoding source\n" % (sourcePath,)])

    def test_check_recursive(self):
        """
        L{check_recursive} descends into each directory, finding Python files
        and reporting problems.
        """
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
        self.assertEqual(warnings, 2)
        self.assertEqual(
            sorted(log),
            sorted([('flake', str(UnusedImport(file1, Node(1), 'baz'))),
                    ('flake',
                     str(UnusedImport(file2, Node(1), 'contraband')))]))


class IntegrationTests(TestCase):
    """
    Tests of the frosted script that actually spawn the script.
    """

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.tempfilepath = os.path.join(self.tempdir, 'temp')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def getFrostedBinary(self):
        """
        Return the path to the frosted binary.
        """
        import frosted
        package_dir = os.path.dirname(frosted.__file__)
        return os.path.join(package_dir, '..', 'bin', 'frosted')

    def runFrosted(self, paths, stdin=None):
        """
        Launch a subprocess running C{frosted}.

        @param args: Command-line arguments to pass to frosted.
        @param kwargs: Options passed on to C{subprocess.Popen}.
        @return: C{(returncode, stdout, stderr)} of the completed frosted
            process.
        """
        env = native_dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(sys.path)
        command = [sys.executable, self.getFrostedBinary()]
        command.extend(paths)
        if stdin:
            p = subprocess.Popen(command, env=env, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdout, stderr) = p.communicate(stdin)
        else:
            p = subprocess.Popen(command, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdout, stderr) = p.communicate()
        rv = p.wait()
        if PY3:
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')

        return (stdout, stderr, rv)

    def test_goodFile(self):
        """
        When a Python source file is all good, the return code is zero and no
        messages are printed to either stdout or stderr.
        """
        fd = open(self.tempfilepath, 'a')
        fd.close()
        d = self.runFrosted([self.tempfilepath])
        self.assertEqual(d, ('', '', 0))

    def test_fileWithFlakes(self):
        """
        When a Python source file has warnings, the return code is non-zero
        and the warnings are printed to stdout.
        """
        fd = open(self.tempfilepath, 'wb')
        fd.write("import contraband\n".encode('ascii'))
        fd.close()
        d = self.runFrosted([self.tempfilepath])
        expected = UnusedImport(self.tempfilepath, Node(1), 'contraband'.encode('ascii'))
        self.assertEqual(d, ("%s\n" % expected, '', 1))

    def test_errors(self):
        """
        When frosted finds errors with the files it's given, (if they don't
        exist, say), then the return code is non-zero and the errors are
        printed to stderr.
        """
        d = self.runFrosted([self.tempfilepath])
        error_msg = '%s: No such file or directory\n' % (self.tempfilepath,)
        self.assertEqual(d, ('', error_msg, 1))

    def test_readFromStdin(self):
        """
        If no arguments are passed to C{frosted} then it reads from stdin.
        """
        d = self.runFrosted([], stdin='import contraband'.encode('ascii'))
        expected = UnusedImport('<stdin>', Node(1), 'contraband'.encode('ascii'))
        self.assertEqual(d, (str(expected) + "\n", '', 1))
