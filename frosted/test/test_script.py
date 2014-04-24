"""frosted/test/test_script.py.

Tests functionality (integration testing) that require starting a full frosted instance against input files

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

from __future__ import absolute_import, division, print_function

import os
import shutil
import subprocess
import sys
import tempfile

import pytest
from pies.overrides import *

import frosted
from frosted.api import iter_source_code
from frosted.messages import UnusedImport

from .utils import Node

FROSTED_BINARY = os.path.join(os.path.dirname(frosted.__file__), 'main.py')


def setup_function(function):
    globals()['TEMP_DIR'] = tempfile.mkdtemp()
    globals()['TEMP_FILE_PATH'] = os.path.join(TEMP_DIR, 'temp')


def teardown_function(function):
    shutil.rmtree(TEMP_DIR)


def make_empty_file(*parts):
    assert parts
    fpath = os.path.join(TEMP_DIR, *parts)
    fd = open(fpath, 'a')
    fd.close()
    return fpath


def test_emptyDirectory():
    """There are no Python files in an empty directory."""
    assert list(iter_source_code([TEMP_DIR])) == []


def test_singleFile():
    """If the directory contains one Python file - iter_source_code will find it"""
    childpath = make_empty_file('foo.py')
    assert list(iter_source_code([TEMP_DIR])) == [childpath]


def test_onlyPythonSource():
    """Files that are not Python source files are not included."""
    make_empty_file('foo.pyc')
    assert list(iter_source_code([TEMP_DIR])) == []


def test_recurses():
    """If the Python files are hidden deep down in child directories, we will find them."""
    os.mkdir(os.path.join(TEMP_DIR, 'foo'))
    apath = make_empty_file('foo', 'a.py')
    os.mkdir(os.path.join(TEMP_DIR, 'bar'))
    bpath = make_empty_file('bar', 'b.py')
    cpath = make_empty_file('c.py')
    assert sorted(iter_source_code([TEMP_DIR])) == sorted([apath, bpath, cpath])


def test_multipleDirectories():
    """iter_source_code can be given multiple directories - it will recurse into each of them"""
    foopath = os.path.join(TEMP_DIR, 'foo')
    barpath = os.path.join(TEMP_DIR, 'bar')
    os.mkdir(foopath)
    apath = make_empty_file('foo', 'a.py')
    os.mkdir(barpath)
    bpath = make_empty_file('bar', 'b.py')
    assert sorted(iter_source_code([foopath, barpath])) == sorted([apath, bpath])


def test_explicitFiles():
    """If one of the paths given to iter_source_code is not a directory but a
    file, it will include that in its output."""
    epath = make_empty_file('e.py')
    assert list(iter_source_code([epath])) == [epath]


def run_frosted(paths, stdin=None):
    """Launch a subprocess running frosted."""
    env = native_dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join(sys.path)
    command = [sys.executable, FROSTED_BINARY]
    command.extend(paths)
    if stdin:
        p = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate(stdin)
    else:
        p = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
    rv = p.wait()
    if PY3:
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')

    return (stdout, stderr, rv)


def test_goodFile():
    """When a Python source file is all good, the return code is zero and no

    messages are printed to either stdout or stderr.

    """
    fd = open(TEMP_FILE_PATH, 'a')
    fd.close()
    d = run_frosted([TEMP_FILE_PATH])
    assert d == ('', '', 0)


def test_fileWithFlakes():
    """ When a Python source file has warnings,

    the return code is non-zero and the warnings are printed to stdout

    """
    fd = open(TEMP_FILE_PATH, 'wb')
    fd.write("import contraband\n".encode('ascii'))
    fd.close()
    d = run_frosted([TEMP_FILE_PATH])
    expected = UnusedImport(TEMP_FILE_PATH, Node(1), 'contraband')
    assert d[0].strip() == expected.message.strip()


@pytest.mark.skipif("sys.version_info >= (3,)")
def test_non_unicode_slash_u():
    """ Ensure \ u doesn't cause a unicode decode error """
    fd = open(TEMP_FILE_PATH, 'wb')
    fd.write('"""Example: C:\\foobar\\unit-tests\\test.py"""'.encode('ascii'))
    fd.close()
    d = run_frosted([TEMP_FILE_PATH])
    assert d == ('', '', 0)


def test_errors():
    """ When frosted finds errors with the files it's given, (if they don't exist, say),

    then the return code is non-zero and the errors are printed to stderr

    """
    d = run_frosted([TEMP_FILE_PATH, '-r'])
    error_msg = '%s: No such file or directory\n' % (TEMP_FILE_PATH,)
    assert d == ('', error_msg, 1)


def test_readFromStdin():
    """If no arguments are passed to C{frosted} then it reads from stdin."""
    d = run_frosted(['-'], stdin='import contraband'.encode('ascii'))

    expected = UnusedImport('<stdin>', Node(1), 'contraband')
    assert d[0].strip() == expected.message.strip()


@pytest.mark.skipif("sys.version_info >= (3,)")
def test_print_statement_python2():
    d = run_frosted(['-'], stdin='print "Hello, Frosted"'.encode('ascii'))
    assert d == ('', '', 0)
