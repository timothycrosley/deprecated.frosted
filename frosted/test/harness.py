
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import textwrap

from frosted import checker
from pies import unittest
from pies.overrides import *

PyCF_ONLY_AST = 1024
__all__ = ['TestCase']


class TestCase(unittest.TestCase):

    def flakes(self, input, *expectedOutputs, **kw):
        tree = compile(textwrap.dedent(input), "<test>", "exec", PyCF_ONLY_AST)
        results = checker.Checker(tree, **kw)
        outputs = [type(message) for message in results.messages]
        expectedOutputs = list(expectedOutputs)
        outputs.sort(key=lambda t: t.__name__)
        expectedOutputs.sort(key=lambda t: t.__name__)
        self.assertEqual(outputs, expectedOutputs, ('\n'
                                                    'for input:\n'
                                                    '%s\n'
                                                    'expected outputs:\n'
                                                    '%r\n'
                                                    'but got:\n'
                                                    '%s') % (input, expectedOutputs,
                                                             '\n'.join([str(o) for o in results.messages])))
        return results
