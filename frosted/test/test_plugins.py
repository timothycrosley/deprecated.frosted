from __future__ import absolute_import, division, print_function, unicode_literals

import textwrap
import pkg_resources
from mock import MagicMock, patch

from pies.overrides import *

from frosted import checker

PyCF_ONLY_AST = 1024

@patch.object(checker.Checker, 'report')
def test_plugins(m_report):
    """ Plugins should be invoked by their "check" method
    """
    tree = compile(textwrap.dedent(""), "<test>", "exec", PyCF_ONLY_AST)
    m_report.return_value = None
    m_check = MagicMock(name="check", return_value=[(MagicMock(), None, (), {})])
    m_checker = MagicMock(name="checker", check=m_check)
    m_load = MagicMock(name="load", return_value=m_checker)
    m_plugin = MagicMock(name="plugin", load=m_load)

    with patch.object(pkg_resources, 'iter_entry_points', return_value=[m_plugin]) as mock_ep:
        checker.Checker(tree, "")

    assert m_check.assert_called()
    assert m_report.assert_called()
