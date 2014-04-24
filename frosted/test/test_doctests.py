from __future__ import absolute_import, division, print_function, unicode_literals

import textwrap

import pytest
from pies.overrides import *

from frosted import messages as m

from .utils import flakes


def doctestify(input):
    lines = []
    for line in textwrap.dedent(input).splitlines():
        if line.strip() == '':
            pass
        elif (line.startswith(' ') or
                line.startswith('except:') or
                line.startswith('except ') or
                line.startswith('finally:') or
                line.startswith('else:') or
                line.startswith('elif ')):
            line = "... %s" % line
        else:
            line = ">>> %s" % line
        lines.append(line)
    doctestificator = textwrap.dedent('''\
                def doctest_something():
                    """
                        %s
                    """
                ''')
    return doctestificator % "\n       ".join(lines)


def test_doubleNestingReportsClosestName():
    """Lines in doctest are a bit different so we can't use the test from TestUndefinedNames."""
    exc = flakes('''
        def doctest_stuff():
            """
                >>> def a():
                ...     x = 1
                ...     def b():
                ...         x = 2 # line 7 in the file
                ...         def c():
                ...             x
                ...             x = 3
                ...             return x
                ...         return x
                ...     return x

            """
        ''', m.UndefinedLocal, run_doctests=True).messages[0]

    assert "local variable 'x'" in exc.message and 'line 7' in exc.message


def test_importBeforeDoctest():
    flakes("""
            import foo

            def doctest_stuff():
                '''
                    >>> foo
                '''
            """, run_doctests=True)


@pytest.mark.skipif("'todo'")
def test_importBeforeAndInDoctest():
    flakes('''
            import foo

            def doctest_stuff():
                """
                    >>> import foo
                    >>> foo
                """

            foo
            ''', m.Redefined, run_doctests=True)


def test_importInDoctestAndAfter():
    flakes('''
            def doctest_stuff():
                """
                    >>> import foo
                    >>> foo
                """

            import foo
            foo()
            ''', run_doctests=True)


def test_offsetInDoctests():
    exc = flakes('''

            def doctest_stuff():
                """
                    >>> x # line 5
                """

            ''', m.UndefinedName, run_doctests=True).messages[0]
    assert exc.lineno == 5
    assert exc.col == 12


def test_ignoreErrorsByDefault():
    flakes('''

            def doctest_stuff():
                """
                    >>> x # line 5
                """

            ''')

def test_offsetInLambdasInDoctests():
    exc = flakes('''

            def doctest_stuff():
                """
                    >>> lambda: x # line 5
                """

            ''', m.UndefinedName, run_doctests=True).messages[0]
    assert exc.lineno == 5
    assert exc.col == 20


def test_offsetAfterDoctests():
    exc = flakes('''

            def doctest_stuff():
                """
                    >>> x = 5
                """

            x

            ''', m.UndefinedName, run_doctests=True).messages[0]
    assert exc.lineno == 8
    assert exc.col == 0


def test_syntax_errorInDoctest():
    exceptions = flakes(
            '''
            def doctest_stuff():
                """
                    >>> from # line 4
                    >>> fortytwo = 42
                    >>> except Exception:
                """
            ''',
            m.DoctestSyntaxError,
            m.DoctestSyntaxError, run_doctests=True).messages
    exc = exceptions[0]
    assert exc.lineno == 4
    assert exc.col == 26
    exc = exceptions[1]
    assert exc.lineno == 6
    assert exc.col == 18


def test_indentationErrorInDoctest():
    exc = flakes('''
            def doctest_stuff():
                """
                    >>> if True:
                    ... pass
                """
            ''', m.DoctestSyntaxError, run_doctests=True).messages[0]
    assert exc.lineno == 5
    assert exc.col == 16


def test_offsetWithMultiLineArgs():
    (exc1, exc2) = flakes(
            '''
            def doctest_stuff(arg1,
                                arg2,
                                arg3):
                """
                    >>> assert
                    >>> this
                """
            ''',
        m.DoctestSyntaxError,
        m.UndefinedName, run_doctests=True).messages
    assert exc1.lineno == 6
    assert exc1.col == 19
    assert exc2.lineno == 7
    assert exc2.col == 12


def test_doctestCanReferToFunction():
    flakes("""
            def foo():
                '''
                    >>> foo
                '''
            """, run_doctests=True)


def test_doctestCanReferToClass():
    flakes("""
            class Foo():
                '''
                    >>> Foo
                '''
                def bar(self):
                    '''
                        >>> Foo
                    '''
            """, run_doctests=True)


def test_noOffsetSyntaxErrorInDoctest():
    exceptions = flakes('''
            def buildurl(base, *args, **kwargs):
                """
                >>> buildurl('/blah.php', ('a', '&'), ('b', '=')
                '/blah.php?a=%26&b=%3D'
                >>> buildurl('/blah.php', a='&', 'b'='=')
                '/blah.php?b=%3D&a=%26'
                """
                pass
            ''',
        m.DoctestSyntaxError,
        m.DoctestSyntaxError, run_doctests=True).messages
    exc = exceptions[0]
    assert exc.lineno == 4
    exc = exceptions[1]
    assert exc.lineno == 6
