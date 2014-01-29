"""frosted/reporter.py.

Defines how errors found by frosted should be displayed to the user

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

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from collections import namedtuple

from pies.overrides import *


class Reporter(namedtuple('Reporter', ('stdout', 'stderr'))):
    """Formats the results of frosted checks and then presents them to the user."""

    def unexpected_error(self, filename, msg):
        """Output an unexpected_error specific to the provided filename."""
        self.stderr.write("%s: %s\n" % (filename, msg))

    def flake(self, message):
        """Print an error message to stdout."""
        self.stdout.write(str(message))
        self.stdout.write('\n')

Default = Reporter(sys.stdout, sys.stderr)
