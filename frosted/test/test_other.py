"""Tests for various Frosted behavior."""

from __future__ import absolute_import, division, print_function, unicode_literals

from sys import version_info

import pytest
from pies.overrides import *

from frosted import messages as m

from .utils import flakes


def test_duplicateArgs():
    flakes('def fu(bar, bar): pass', m.DuplicateArgument)


@pytest.mark.skipif("'todo: this requires finding all assignments in the function body first'")
def test_localReferencedBeforeAssignment():
    flakes('''
    a = 1
    def f():
        a; a=1
    f()
    ''', m.UndefinedName)


def test_redefinedInListComp():
    """Test that shadowing a variable in a list comprehension raises a warning."""
    flakes('''
    a = 1
    [1 for a, b in [(1, 2)]]
    ''', m.RedefinedInListComp)
    flakes('''
    class A:
        a = 1
        [1 for a, b in [(1, 2)]]
    ''', m.RedefinedInListComp)
    flakes('''
    def f():
        a = 1
        [1 for a, b in [(1, 2)]]
    ''', m.RedefinedInListComp)
    flakes('''
    [1 for a, b in [(1, 2)]]
    [1 for a, b in [(1, 2)]]
    ''')
    flakes('''
    for a, b in [(1, 2)]:
        pass
    [1 for a, b in [(1, 2)]]
    ''')


def test_redefinedInGenerator():
    """Test that reusing a variable in a generator does not raise a warning."""
    flakes('''
    a = 1
    (1 for a, b in [(1, 2)])
    ''')
    flakes('''
    class A:
        a = 1
        list(1 for a, b in [(1, 2)])
    ''')
    flakes('''
    def f():
        a = 1
        (1 for a, b in [(1, 2)])
    ''', m.UnusedVariable)
    flakes('''
    (1 for a, b in [(1, 2)])
    (1 for a, b in [(1, 2)])
    ''')
    flakes('''
    for a, b in [(1, 2)]:
        pass
    (1 for a, b in [(1, 2)])
    ''')


@pytest.mark.skipif('''version_info < (2, 7)''')
def test_redefinedInSetComprehension():
    """Test that reusing a variable in a set comprehension does not raise a warning."""
    flakes('''
    a = 1
    {1 for a, b in [(1, 2)]}
    ''')
    flakes('''
    class A:
        a = 1
        {1 for a, b in [(1, 2)]}
    ''')
    flakes('''
    def f():
        a = 1
        {1 for a, b in [(1, 2)]}
    ''', m.UnusedVariable)
    flakes('''
    {1 for a, b in [(1, 2)]}
    {1 for a, b in [(1, 2)]}
    ''')
    flakes('''
    for a, b in [(1, 2)]:
        pass
    {1 for a, b in [(1, 2)]}
    ''')


@pytest.mark.skipif('''version_info < (2, 7)''')
def test_redefinedInDictComprehension():
    """Test that reusing a variable in a dict comprehension does not raise a warning."""
    flakes('''
    a = 1
    {1: 42 for a, b in [(1, 2)]}
    ''')
    flakes('''
    class A:
        a = 1
        {1: 42 for a, b in [(1, 2)]}
    ''')
    flakes('''
    def f():
        a = 1
        {1: 42 for a, b in [(1, 2)]}
    ''', m.UnusedVariable)
    flakes('''
    {1: 42 for a, b in [(1, 2)]}
    {1: 42 for a, b in [(1, 2)]}
    ''')
    flakes('''
    for a, b in [(1, 2)]:
        pass
    {1: 42 for a, b in [(1, 2)]}
    ''')


def test_redefinedFunction():
    """Test that shadowing a function definition with another one raises a warning."""
    flakes('''
    def a(): pass
    def a(): pass
    ''', m.RedefinedWhileUnused)


def test_redefinedClassFunction():
    """Test that shadowing a function definition in a class suite with another one raises a warning."""
    flakes('''
    class A:
        def a(): pass
        def a(): pass
    ''', m.RedefinedWhileUnused)


def test_redefinedIfElseFunction():
    """Test that shadowing a function definition twice in an if and else block does not raise a warning."""
    flakes('''
    if True:
        def a(): pass
    else:
        def a(): pass
    ''')


def test_redefinedIfFunction():
    """Test that shadowing a function definition within an if block raises a warning."""
    flakes('''
    if True:
        def a(): pass
        def a(): pass
    ''', m.RedefinedWhileUnused)


def test_redefinedTryExceptFunction():
    """Test that shadowing a function definition twice in try and except block does not raise a warning."""
    flakes('''
    try:
        def a(): pass
    except Exception:
        def a(): pass
    ''')


def test_redefinedTryFunction():
    """Test that shadowing a function definition within a try block raises a warning."""
    flakes('''
    try:
        def a(): pass
        def a(): pass
    except Exception:
        pass
    ''', m.RedefinedWhileUnused)


def test_redefinedIfElseInListComp():
    """Test that shadowing a variable in a list comprehension in an if and else block does not raise a warning."""
    flakes('''
    if False:
        a = 1
    else:
        [a for a in '12']
    ''')


def test_redefinedElseInListComp():
    """Test that shadowing a variable in a list comprehension in an else (or if) block raises a warning."""
    flakes('''
    if False:
        pass
    else:
        a = 1
        [a for a in '12']
    ''', m.RedefinedInListComp)


def test_functionDecorator():
    """Test that shadowing a function definition with a decorated version of that function does not raise a warning."""
    flakes('''
    from somewhere import somedecorator

    def a(): pass
    a = somedecorator(a)
    ''')


def test_classFunctionDecorator():
    """Test that shadowing a function definition in a class suite with a
    decorated version of that function does not raise a warning.

    """
    flakes('''
    class A:
        def a(): pass
        a = classmethod(a)
    ''')


@pytest.mark.skipif('''version_info < (2, 6)''')
def test_modernProperty():
    flakes("""
    class A:
        @property
        def t():
            pass
        @t.setter
        def t(self, value):
            pass
        @t.deleter
        def t():
            pass
    """)


def test_unaryPlus():
    """Don't die on unary +."""
    flakes('+1')


def test_undefinedBaseClass():
    """If a name in the base list of a class definition is undefined, a warning is emitted."""
    flakes('''
    class foo(foo):
        pass
    ''', m.UndefinedName)


def test_classNameUndefinedInClassBody():
    """If a class name is used in the body of that class's definition and the

    name is not already defined, a warning is emitted.

    """
    flakes('''
    class foo:
        foo
    ''', m.UndefinedName)


def test_classNameDefinedPreviously():
    """If a class name is used in the body of that class's definition and the
    name was previously defined in some other way, no warning is emitted.

    """
    flakes('''
    foo = None
    class foo:
        foo
    ''')


def test_classRedefinition():
    """If a class is defined twice in the same module, a warning is emitted."""
    flakes('''
    class Foo:
        pass
    class Foo:
        pass
    ''', m.RedefinedWhileUnused)


def test_functionRedefinedAsClass():
    """If a function is redefined as a class, a warning is emitted."""
    flakes('''
    def Foo():
        pass
    class Foo:
        pass
    ''', m.RedefinedWhileUnused)


def test_classRedefinedAsFunction():
    """If a class is redefined as a function, a warning is emitted."""
    flakes('''
    class Foo:
        pass
    def Foo():
        pass
    ''', m.RedefinedWhileUnused)


@pytest.mark.skipif("'todo: Too hard to make this warn but other cases stay silent'")
def test_doubleAssignment():
    """If a variable is re-assigned to without being used, no warning is emitted."""
    flakes('''
    x = 10
    x = 20
    ''', m.RedefinedWhileUnused)


def test_doubleAssignmentConditionally():
    """If a variable is re-assigned within a conditional, no warning is emitted."""
    flakes('''
    x = 10
    if True:
        x = 20
    ''')


def test_doubleAssignmentWithUse():
    """If a variable is re-assigned to after being used, no warning is emitted."""
    flakes('''
    x = 10
    y = x * 2
    x = 20
    ''')


def test_comparison():
    """If a defined name is used on either side of any of the six comparison operators, no warning is emitted."""
    flakes('''
    x = 10
    y = 20
    x < y
    x <= y
    x == y
    x != y
    x >= y
    x > y
    ''')


def test_identity():
    """If a defined name is used on either side of an identity test, no warning is emitted."""
    flakes('''
    x = 10
    y = 20
    x is y
    x is not y
    ''')


def test_containment():
    """If a defined name is used on either side of a containment test, no warning is emitted."""
    flakes('''
    x = 10
    y = 20
    x in y
    x not in y
    ''')


def test_loopControl():
    """break and continue statements are supported."""
    flakes('''
    for x in [1, 2]:
        break
    ''')
    flakes('''
    for x in [1, 2]:
        continue
    ''')


def test_ellipsis():
    """Ellipsis in a slice is supported."""
    flakes('''
    [1, 2][...]
    ''')


def test_extendedSlice():
    """Extended slices are supported."""
    flakes('''
    x = 3
    [1, 2][x,:]
    ''')


def test_varAugmentedAssignment():
    """Augmented assignment of a variable is supported.

    We don't care about var refs.

    """
    flakes('''
    foo = 0
    foo += 1
    ''')


def test_attrAugmentedAssignment():
    """Augmented assignment of attributes is supported.

    We don't care about attr refs.

    """
    flakes('''
    foo = None
    foo.bar += foo.baz
    ''')


def test_unusedVariable():
    """Warn when a variable in a function is assigned a value that's never used."""
    flakes('''
    def a():
        b = 1
    ''', m.UnusedVariable)


def test_unusedVariableAsLocals():
    """Using locals() it is perfectly valid to have unused variables."""
    flakes('''
    def a():
        b = 1
        return locals()
    ''')


def test_unusedVariableNoLocals():
    """Using locals() in wrong scope should not matter."""
    flakes('''
    def a():
        locals()
        def a():
            b = 1
            return
    ''', m.UnusedVariable)


def test_assignToGlobal():
    """Assigning to a global and then not using that global is perfectly
    acceptable.

    Do not mistake it for an unused local variable.

    """
    flakes('''
    b = 0
    def a():
        global b
        b = 1
    ''')


@pytest.mark.skipif('''version_info < (3,)''')
def test_assignToNonlocal():
    """Assigning to a nonlocal and then not using that binding is perfectly
    acceptable.

    Do not mistake it for an unused local variable.

    """
    flakes('''
    b = b'0'
    def a():
        nonlocal b
        b = b'1'
    ''')


def test_assignToMember():
    """Assigning to a member of another object and then not using that member
    variable is perfectly acceptable.

    Do not mistake it for an unused local variable.

    """
    # XXX: Adding this test didn't generate a failure. Maybe not
    # necessary?
    flakes('''
    class b:
        pass
    def a():
        b.foo = 1
    ''')


def test_assignInForLoop():
    """Don't warn when a variable in a for loop is assigned to but not used."""
    flakes('''
    def f():
        for i in range(10):
            pass
    ''')


def test_assignInListComprehension():
    """Don't warn when a variable in a list comprehension is assigned to but not used."""
    flakes('''
    def f():
        [None for i in range(10)]
    ''')


def test_generatorExpression():
    """Don't warn when a variable in a generator expression is assigned to but not used."""
    flakes('''
    def f():
        (None for i in range(10))
    ''')


def test_assignmentInsideLoop():
    """Don't warn when a variable assignment occurs lexically after its use."""
    flakes('''
    def f():
        x = None
        for i in range(10):
            if i > 2:
                return x
            x = i * 2
    ''')


def test_tupleUnpacking():
    """Don't warn when a variable included in tuple unpacking is unused.

    It's very common for variables in a tuple unpacking assignment to be unused in good Python code, so warning will
    only create false positives.

    """
    flakes('''
    def f():
        (x, y) = 1, 2
    ''')


def test_listUnpacking():
    """Don't warn when a variable included in list unpacking is unused."""
    flakes('''
    def f():
        [x, y] = [1, 2]
    ''')


def test_closedOver():
    """Don't warn when the assignment is used in an inner function."""
    flakes('''
    def barMaker():
        foo = 5
        def bar():
            return foo
        return bar
    ''')


def test_doubleClosedOver():
    """Don't warn when the assignment is used in an inner function, even if
    that inner function itself is in an inner function."""
    flakes('''
    def barMaker():
        foo = 5
        def bar():
            def baz():
                return foo
        return bar
    ''')


def test_tracebackhideSpecialVariable():
    """Do not warn about unused local variable __tracebackhide__, which is a
    special variable for py.test."""
    flakes("""
        def helper():
            __tracebackhide__ = True
    """)


def test_ifexp():
    """Test C{foo if bar else baz} statements."""
    flakes("a = 'moo' if True else 'oink'")
    flakes("a = foo if True else 'oink'", m.UndefinedName)
    flakes("a = 'moo' if True else bar", m.UndefinedName)


def test_withStatementNoNames():
    """No warnings are emitted for using inside or after a nameless  statement a name defined beforehand."""
    flakes('''
    from __future__ import with_statement
    bar = None
    with open("foo"):
        bar
    bar
    ''')


def test_withStatementSingleName():
    """No warnings are emitted for using a name defined by a  statement within the suite or afterwards."""
    flakes('''
    from __future__ import with_statement
    with open('foo') as bar:
        bar
    bar
    ''')


def test_withStatementAttributeName():
    """No warnings are emitted for using an attribute as the target of a  statement."""
    flakes('''
    from __future__ import with_statement
    import foo
    with open('foo') as foo.bar:
        pass
    ''')


def test_withStatementSubscript():
    """No warnings are emitted for using a subscript as the target of a  statement."""
    flakes('''
    from __future__ import with_statement
    import foo
    with open('foo') as foo[0]:
        pass
    ''')


def test_withStatementSubscriptUndefined():
    """An undefined name warning is emitted if the subscript used as the target of a with statement is not defined."""
    flakes('''
    from __future__ import with_statement
    import foo
    with open('foo') as foo[bar]:
        pass
    ''', m.UndefinedName)


def test_withStatementTupleNames():
    """No warnings are emitted for using any of the tuple of names defined

    by a statement within the suite or afterwards.

    """
    flakes('''
    from __future__ import with_statement
    with open('foo') as (bar, baz):
        bar, baz
    bar, baz
    ''')


def test_withStatementListNames():
    """No warnings are emitted for using any of the list of names defined by

    a statement within the suite or afterwards.

    """
    flakes('''
    from __future__ import with_statement
    with open('foo') as [bar, baz]:
        bar, baz
    bar, baz
    ''')


def test_withStatementComplicatedTarget():
    """ If the target of a  statement uses any or all of the valid forms
    for that part of the grammar
    (See: http://docs.python.org/reference/compound_stmts.html#the-with-statement),
    the names involved are checked both for definedness and any bindings
    created are respected in the suite of the statement and afterwards.

    """
    flakes('''
    from __future__ import with_statement
    c = d = e = g = h = i = None
    with open('foo') as [(a, b), c[d], e.f, g[h:i]]:
        a, b, c, d, e, g, h, i
    a, b, c, d, e, g, h, i
    ''')


def test_withStatementSingleNameUndefined():
    """An undefined name warning is emitted if the name first defined by a statement is used before the  statement."""
    flakes('''
    from __future__ import with_statement
    bar
    with open('foo') as bar:
        pass
    ''', m.UndefinedName)


def test_withStatementTupleNamesUndefined():
    """ An undefined name warning is emitted if a name first defined by a the
    tuple-unpacking form of the  statement is used before the statement.

    """
    flakes('''
    from __future__ import with_statement
    baz
    with open('foo') as (bar, baz):
        pass
    ''', m.UndefinedName)


def test_withStatementSingleNameRedefined():
    """A redefined name warning is emitted if a name bound by an import is
    rebound by the name defined by a  statement.

    """
    flakes('''
    from __future__ import with_statement
    import bar
    with open('foo') as bar:
        pass
    ''', m.RedefinedWhileUnused)


def test_withStatementTupleNamesRedefined():
    """ A redefined name warning is emitted if a name bound by an import is
    rebound by one of the names defined by the tuple-unpacking form of a
    statement.

    """
    flakes('''
    from __future__ import with_statement
    import bar
    with open('foo') as (bar, baz):
        pass
    ''', m.RedefinedWhileUnused)


def test_withStatementUndefinedInside():
    """An undefined name warning is emitted if a name is used inside the body
    of a  statement without first being bound.

    """
    flakes('''
    from __future__ import with_statement
    with open('foo') as bar:
        baz
    ''', m.UndefinedName)


def test_withStatementNameDefinedInBody():
    """A name defined in the body of a  statement can be used after the body ends without warning."""
    flakes('''
    from __future__ import with_statement
    with open('foo') as bar:
        baz = 10
    baz
    ''')


def test_withStatementUndefinedInExpression():
    """An undefined name warning is emitted if a name in the I{test} expression of a  statement is undefined."""
    flakes('''
    from __future__ import with_statement
    with bar as baz:
        pass
    ''', m.UndefinedName)

    flakes('''
    from __future__ import with_statement
    with bar as bar:
        pass
    ''', m.UndefinedName)


@pytest.mark.skipif('''version_info < (2, 7)''')
def test_dictComprehension():
    """Dict comprehensions are properly handled."""
    flakes('''
    a = {1: x for x in range(10)}
    ''')


@pytest.mark.skipif('''version_info < (2, 7)''')
def test_setComprehensionAndLiteral():
    """Set comprehensions are properly handled."""
    flakes('''
    a = {1, 2, 3}
    b = {x for x in range(10)}
    ''')


def test_exceptionUsedInExcept():
    as_exc = ', ' if version_info < (2, 6) else ' as '
    flakes('''
    try: pass
    except Exception%se: e
    ''' % as_exc)

    flakes('''
    def download_review():
        try: pass
        except Exception%se: e
    ''' % as_exc)


def test_exceptWithoutNameInFunction():
    """Don't issue false warning when an unnamed exception is used.

    Previously, there would be a false warning, but only when the try..except was in a function

    """
    flakes('''
    import tokenize
    def foo():
        try: pass
        except tokenize.TokenError: pass
    ''')


def test_exceptWithoutNameInFunctionTuple():
    """Don't issue false warning when an unnamed exception is used.

    This example catches a tuple of exception types.

    """
    flakes('''
    import tokenize
    def foo():
        try: pass
        except (tokenize.TokenError, IndentationError): pass
    ''')


def test_augmentedAssignmentImportedFunctionCall():
    """Consider a function that is called on the right part of an augassign operation to be used."""
    flakes('''
    from foo import bar
    baz = 0
    baz += bar()
    ''')


@pytest.mark.skipif('''version_info < (3, 3)''')
def test_yieldFromUndefined():
    """Test yield from statement."""
    flakes('''
    def bar():
        yield from foo()
    ''', m.UndefinedName)


def test_bareExcept():
    """
        Issue a warning when using bare except:.
    """
    flakes('''
        try:
            pass
        except:
            pass
        ''', m.BareExcept)


def test_access_debug():
    """Test accessing __debug__ returns no errors"""
    flakes('''
    if __debug__:
        print("success!")
        print(__debug__)
    ''')
