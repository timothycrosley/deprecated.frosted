from __future__ import absolute_import, division, print_function, unicode_literals

from sys import version_info

import pytest
from pies.overrides import *

from frosted import messages as m

from .utils import flakes


@pytest.mark.skipif("version_info >= (3,)")
def test_return():
    flakes('''
    class a:
        def b():
            for x in a.c:
                if x:
                    yield x
            return a
    ''', m.ReturnWithArgsInsideGenerator)


@pytest.mark.skipif("version_info >= (3,)")
def test_returnNone():
    flakes('''
    def a():
        yield 12
        return None
    ''', m.ReturnWithArgsInsideGenerator)


@pytest.mark.skipif("version_info >= (3,)")
def test_returnYieldExpression():
    flakes('''
    def a():
        b = yield a
        return b
    ''', m.ReturnWithArgsInsideGenerator)


@pytest.mark.skipif("version_info >= (3,)")
def test_return_with_args_inside_generator_not_duplicated():
    # doubly nested - should still only complain once
    flakes('''
    def f0():
        def f1():
            yield None
            return None
    ''', m.ReturnWithArgsInsideGenerator)

    # triple nested - should still only complain once
    flakes('''
    def f0():
        def f1():
            def f2():
                yield None
                return None
    ''', m.ReturnWithArgsInsideGenerator)


@pytest.mark.skipif("version_info >= (3,)")
def test_no_false_positives_for_return_inside_generator():
    # doubly nested - should still only complain once
    flakes('''
    def f():
        def g():
            yield None
        return g
    ''')
