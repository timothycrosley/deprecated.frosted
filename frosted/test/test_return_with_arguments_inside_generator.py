
from sys import version_info

from frosted import messages as m
from frosted.test.harness import TestCase
from pies.unittest import skipIf
from . import flakes


@skipIf(version_info >= (3,), 'new in Python 3')
def test_return():
    flakes('''
    class a:
        def b():
            for x in a.c:
                if x:
                    yield x
            return a
    ''', m.ReturnWithArgsInsideGenerator)


@skipIf(version_info >= (3,), 'new in Python 3')
def test_returnNone():
    flakes('''
    def a():
        yield 12
        return None
    ''', m.ReturnWithArgsInsideGenerator)


@skipIf(version_info >= (3,), 'new in Python 3')
def test_returnYieldExpression():
    flakes('''
    def a():
        b = yield a
        return b
    ''', m.ReturnWithArgsInsideGenerator)
