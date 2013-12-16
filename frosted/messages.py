"""
    frosted/reporter.py

    Defines the error messages that frosted can output

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

from pies.overrides import *


class Message(object):
    message = ''
    message_args = ()

    def __init__(self, filename, loc):
        self.filename = filename
        self.lineno = loc.lineno
        self.col = getattr(loc, 'col_offset', 0)

    def __str__(self):
        return '%s:%s: %s' % (self.filename, self.lineno, self.message % self.message_args)


class UnusedImport(Message):
    message = '%r imported but unused'

    def __init__(self, filename, loc, name):
        Message.__init__(self, filename, loc)
        self.message_args = (name,)


class RedefinedWhileUnused(Message):
    message = 'redefinition of unused %r from line %r'

    def __init__(self, filename, loc, name, orig_loc):
        Message.__init__(self, filename, loc)
        self.message_args = (name, orig_loc.lineno)


class RedefinedInListComp(Message):
    message = 'list comprehension redefines %r from line %r'

    def __init__(self, filename, loc, name, orig_loc):
        Message.__init__(self, filename, loc)
        self.message_args = (name, orig_loc.lineno)


class ImportShadowedByLoopVar(Message):
    message = 'import %r from line %r shadowed by loop variable'

    def __init__(self, filename, loc, name, orig_loc):
        Message.__init__(self, filename, loc)
        self.message_args = (name, orig_loc.lineno)


class ImportStarUsed(Message):
    message = "'from %s import *' used; unable to detect undefined names"

    def __init__(self, filename, loc, modname):
        Message.__init__(self, filename, loc)
        self.message_args = (modname,)


class UndefinedName(Message):
    message = 'undefined name %r'

    def __init__(self, filename, loc, name):
        Message.__init__(self, filename, loc)
        self.message_args = (name,)


class DoctestSyntaxError(Message):
    message = 'syntax error in doctest'

    def __init__(self, filename, loc, position=None):
        Message.__init__(self, filename, loc)
        if position:
            (self.lineno, self.col) = position
        self.message_args = ()


class UndefinedExport(Message):
    message = 'undefined name %r in __all__'

    def __init__(self, filename, loc, name):
        Message.__init__(self, filename, loc)
        self.message_args = (name,)


class UndefinedLocal(Message):
    message = ('local variable %r (defined in enclosing scope on line %r) '
               'referenced before assignment')

    def __init__(self, filename, loc, name, orig_loc):
        Message.__init__(self, filename, loc)
        self.message_args = (name, orig_loc.lineno)


class DuplicateArgument(Message):
    message = 'duplicate argument %r in function definition'

    def __init__(self, filename, loc, name):
        Message.__init__(self, filename, loc)
        self.message_args = (name,)


class Redefined(Message):
    message = 'redefinition of %r from line %r'

    def __init__(self, filename, loc, name, orig_loc):
        Message.__init__(self, filename, loc)
        self.message_args = (name, orig_loc.lineno)


class LateFutureImport(Message):
    message = 'future import(s) %r after other statements'

    def __init__(self, filename, loc, names):
        Message.__init__(self, filename, loc)
        self.message_args = (names,)


class UnusedVariable(Message):
    """
        Indicates that a variable has been explicity assigned to but not actually
        used.
    """
    message = 'local variable %r is assigned to but never used'

    def __init__(self, filename, loc, names):
        Message.__init__(self, filename, loc)
        self.message_args = (names,)


class MultipleValuesForArgument(Message):
    message = '%s() got multiple values for argument %r'
    def __init__(self, filename, loc, functionname, argname):
        Message.__init__(self, filename, loc)
        self.message_args = (functionname, argname)


class TooFewArguments(Message):
    message = '%s() takes at least %d argument(s)'
    def __init__(self, filename, loc, functionname, minargs):
        Message.__init__(self, filename, loc)
        self.message_args = (functionname, minargs)


class TooManyArguments(Message):
    message = '%s() takes at most %d argument(s)'
    def __init__(self, filename, loc, functionname, maxargs):
        Message.__init__(self, filename, loc)
        self.message_args = (functionname, maxargs)


class UnexpectedArgument(Message):
    message = '%s() got unexpected keyword argument: %r'
    def __init__(self, filename, loc, functionname, argname):
        Message.__init__(self, filename, loc)
        self.message_args = (functionname, argname)


class NeedKwOnlyArgument(Message):
    message = '%s() needs kw-only argument(s): %s'
    def __init__(self, filename, loc, functionname, missing_arguments):
        Message.__init__(self, filename, loc)
        self.message_args = (functionname, missing_arguments)


class ReturnWithArgsInsideGenerator(Message):
    """
        Indicates a return statement with arguments inside a generator.
    """
    message = '\'return\' with argument inside generator'
