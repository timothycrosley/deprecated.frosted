#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from pies.overrides import *

from frosted import messages as m

from .utils import flakes


def test_ok():
    flakes('''
    def foo(a):
        pass
    foo(5)
    ''')

    flakes('''
    def foo(a, b=2):
        pass
    foo(5, b=1)
    ''')


def test_noCheckDecorators():
    flakes('''
    def decorator(f):
        return f
    @decorator
    def foo():
        pass
    foo(42)
    ''')


def test_tooManyArguments():
    flakes('''
    def foo():
        pass
    foo(5)
    ''', m.TooManyArguments)
    flakes('''
    def foo(a, b):
        pass
    foo(5, 6, 7)
    ''', m.TooManyArguments)


def test_tooManyArgumentsVarargs():
    flakes('''
    def foo(a, *args):
        pass
    foo(1, 2, 3)
    ''')


def test_unexpectedArgument():
    flakes('''
    def foo(a):
        pass
    foo(1, b=3)
    ''', m.UnexpectedArgument)

    flakes('''
    def foo(a, *args):
        pass
    foo(1, b=3)
    ''', m.UnexpectedArgument)

    flakes('''
    def foo(a, **kwargs):
        pass
    foo(1, b=3)
    ''')


def test_multipleValuesForArgument():
    flakes('''
    def foo(a):
        pass
    foo(5, a=5)
    ''', m.MultipleValuesForArgument)


def test_tooFewArguments():
    flakes('''
    def foo(a):
        pass
    foo()
    ''', m.TooFewArguments)

    flakes('''
    def foo(a):
        pass
    foo(*[])
    ''')

    flakes('''
    def foo(a):
        pass
    foo(**{})
    ''')


def test_tooFewArgumentsVarArgs():
    flakes('''
    def foo(a, b, *args):
        pass
    foo(1)
    ''', m.TooFewArguments)


if PY3:
    def test_kwOnlyArguments():
        flakes('''
        def foo(a, *, b=0):
            pass
        foo(5, b=2)
        ''')

        flakes('''
        def foo(a, *, b=0):
            pass
        foo(5)
        ''')

        flakes('''
        def foo(a, *, b):
            pass
        foo(5, b=2)
        ''')

        flakes('''
        def foo(a, *, b):
            pass
        foo(5, **{})
        ''')

        flakes('''
        def foo(a, *, b):
            pass
        foo(1)
        ''', m.NeedKwOnlyArgument)

        flakes('''
        def foo(a, *args, b):
            pass
        foo(1, 2, 3, 4)
        ''', m.NeedKwOnlyArgument)
elif PY2:
    def test_compoundArguments():
        flakes('''
        def foo(a, (b, c)):
            pass
        foo(1, [])''')

        flakes('''
        def foo(a, (b, c)):
            pass
        foo(1, 2, 3)''', m.TooManyArguments)

        flakes('''
        def foo(a, (b, c)):
            pass
        foo(1)''', m.TooFewArguments)

        flakes('''
        def foo(a, (b, c)):
            pass
        foo(1, b=2, c=3)''', m.UnexpectedArgument)
