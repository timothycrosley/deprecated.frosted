from __future__ import absolute_import, division, print_function, unicode_literals

import textwrap

from pies.overrides import *

from frosted import messages as m
from pies.unittest import skip
from .utils import flakes as flakes_utils

from frosted.test.harness import TestCase


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


def flakes(input, *args, **kwargs):
    return flakes_utils(doctestify(input), *args, **kwargs)


def test_doubleNestingReportsClosestName():
    """
        Lines in doctest are a bit different so we can't use the test
        from TestUndefinedNames
    """
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
        ''', m.UndefinedLocal).messages[0]
    assert exc.message_args == ('x', 7)


def test_futureImport():
    """
        XXX This test can't work in a doctest
    """


def test_importBeforeDoctest():
    flakes("""
            import foo

            def doctest_stuff():
                '''
                    >>> foo
                '''
            """)


@skip("todo")
def test_importBeforeAndInDoctest():
    flakes('''
            import foo

            def doctest_stuff():
                """
                    >>> import foo
                    >>> foo
                """

            foo
            ''', m.Redefined)


def test_importInDoctestAndAfter():
    flakes('''
            def doctest_stuff():
                """
                    >>> import foo
                    >>> foo
                """

            import foo
            foo()
            ''')


def test_offsetInDoctests():
    flakes('''

            def doctest_stuff():
                """
                    >>> x # line 5
                """

            ''', m.UndefinedName).messages[0]
    assert exc.lineno == 5
    assert exc.col == 12


def test_offsetInLambdasInDoctests():
    flakes('''

            def doctest_stuff():
                """
                    >>> lambda: x # line 5
                """

            ''', m.UndefinedName).messages[0]
    assert exc.lineno == 5
    assert exc.col == 20


def test_offsetAfterDoctests():
    flakes('''

            def doctest_stuff():
                """
                    >>> x = 5
                """

            x

            ''', m.UndefinedName).messages[0]
    assert exc.lineno == 8
    assert exc.col == 0


def test_syntax_errorInDoctest():
    flakes(
            '''
            def doctest_stuff():
                """
                    >>> from # line 4
                    >>> fortytwo = 42
                    >>> except Exception:
                """
            ''',
            m.DoctestSyntaxError,
            m.DoctestSyntaxError,
            m.DoctestSyntaxError).messages
    exc = exceptions[0]
    assert exc.lineno == 4
    assert exc.col == 26
    exc = exceptions[1]
    assert exc.lineno == 5
    assert exc.col == 16
    exc = exceptions[2]
    assert exc.lineno == 6
    assert exc.col == 18


def test_indentationErrorInDoctest():
    flakes('''
            def doctest_stuff():
                """
                    >>> if True:
                    ... pass
                """
            ''', m.DoctestSyntaxError).messages[0]
    assert exc.lineno == 5
    assert exc.col == 16


def test_offsetWithMultiLineArgs():
    flakes(
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
        m.UndefinedName).messages
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
            """)


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
            """)


def test_noOffsetSyntaxErrorInDoctest():
    flakes('''
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
        m.DoctestSyntaxError).messages
    exc = exceptions[0]
    assert exc.lineno == 4
    exc = exceptions[1]
    assert exc.lineno == 6
