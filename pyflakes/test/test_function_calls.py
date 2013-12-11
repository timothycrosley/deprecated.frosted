#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from pyflakes import messages as m
from pyflakes.test import harness

class Test(harness.TestCase):
    def test_ok(self):
        self.flakes('''
        def foo(a):
            pass
        foo(5)
        ''')

        self.flakes('''
        def foo(a, b=2):
            pass
        foo(5, b=1)
        ''')

    def test_noCheckDecorators(self):
        self.flakes('''
        def decorator(f):
            return f
        @decorator
        def foo():
            pass
        foo(42)
        ''')

    def test_tooManyArguments(self):
        self.flakes('''
        def foo():
            pass
        foo(5)
        ''', m.TooManyArguments)
        self.flakes('''
        def foo(a, b):
            pass
        foo(5, 6, 7)
        ''', m.TooManyArguments)

    def test_tooManyArgumentsVarargs(self):
        self.flakes('''
        def foo(a, *args):
            pass
        foo(1, 2, 3)
        ''')

    def test_unexpectedArgument(self):
        self.flakes('''
        def foo(a):
            pass
        foo(1, b=3)
        ''', m.UnexpectedArgument)

        self.flakes('''
        def foo(a, *args):
            pass
        foo(1, b=3)
        ''', m.UnexpectedArgument)

        self.flakes('''
        def foo(a, **kwargs):
            pass
        foo(1, b=3)
        ''')

    def test_multipleValuesForArgument(self):
        self.flakes('''
        def foo(a):
            pass
        foo(5, a=5)
        ''', m.MultipleValuesForArgument)

    def test_tooFewArguments(self):
        self.flakes('''
        def foo(a):
            pass
        foo()
        ''', m.TooFewArguments)

        self.flakes('''
        def foo(a):
            pass
        foo(*[])
        ''')

        self.flakes('''
        def foo(a):
            pass
        foo(**{})
        ''')

    def test_tooFewArgumentsVarArgs(self):
        self.flakes('''
        def foo(a, b, *args):
            pass
        foo(1)
        ''', m.TooFewArguments)

    if sys.version_info[0] == 3:
        def test_kwOnlyArguments(self):
            self.flakes('''
            def foo(a, *, b=0):
                pass
            foo(5, b=2)
            ''')

            self.flakes('''
            def foo(a, *, b=0):
                pass
            foo(5)
            ''')

            self.flakes('''
            def foo(a, *, b):
                pass
            foo(5, b=2)
            ''')

            self.flakes('''
            def foo(a, *, b):
                pass
            foo(5, **{})
            ''')
       
            self.flakes('''
            def foo(a, *, b):
                pass
            foo(1)
            ''', m.NeedKwOnlyArgument)

            self.flakes('''
            def foo(a, *args, b):
                pass
            foo(1, 2, 3, 4)
            ''', m.NeedKwOnlyArgument)

    if sys.version_info[0] == 2:
        def test_compoundArguments(self):
            self.flakes('''
            def foo(a, (b, c)):
                pass
            foo(1, [])''')

            self.flakes('''
            def foo(a, (b, c)):
                pass
            foo(1, 2, 3)''', m.TooManyArguments)

            self.flakes('''
            def foo(a, (b, c)):
                pass
            foo(1)''', m.TooFewArguments)

            self.flakes('''
            def foo(a, (b, c)):
                pass
            foo(1, b=2, c=3)''', m.UnexpectedArgument)
