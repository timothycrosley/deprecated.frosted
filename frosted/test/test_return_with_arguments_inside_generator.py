
from sys import version_info

from frosted import messages as m
from frosted.test.harness import TestCase
from pies.unittest import skipIf


class Test(TestCase):
    @skipIf(version_info >= (3,), 'new in Python 3')
    def test_return(self):
        self.flakes('''
        class a:
            def b():
                for x in a.c:
                    if x:
                        yield x
                return a
        ''', m.ReturnWithArgsInsideGenerator)

    @skipIf(version_info >= (3,), 'new in Python 3')
    def test_returnNone(self):
        self.flakes('''
        def a():
            yield 12
            return None
        ''', m.ReturnWithArgsInsideGenerator)

    @skipIf(version_info >= (3,), 'new in Python 3')
    def test_returnYieldExpression(self):
        self.flakes('''
        def a():
            b = yield a
            return b
        ''', m.ReturnWithArgsInsideGenerator)
