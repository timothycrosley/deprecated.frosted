from __future__ import absolute_import, division, print_function, unicode_literals

from sys import version_info

import pytest
from pies.overrides import *

from _ast import PyCF_ONLY_AST
from frosted import messages as m
from frosted import checker

from.utils import flakes


def test_undefined():
    flakes('bar', m.UndefinedName)


def test_definedInListComp():
    flakes('[a for a in range(10) if a]')


def test_functionsNeedGlobalScope():
    flakes('''
    class a:
        def b():
            fu
    fu = 1
    ''')


def test_builtins():
    flakes('range(10)')


def test_builtinWindowsError():
    """WindowsError is sometimes a builtin name, so no warning is emitted for using it."""
    flakes('WindowsError')


def test_magicGlobalsFile():
    """Use of the __file magic global should not emit an undefined name
    warning."""
    flakes('__file__')


def test_magicGlobalsBuiltins():
    """Use of the __builtins magic global should not emit an undefined name warning."""
    flakes('__builtins__')


def test_magicGlobalImport():
    """Use of the __import__ magic global should not emit an undefined name warning."""
    flakes('__import__')

def test_magicGlobalsName():
    """Use of the __name magic global should not emit an undefined name warning."""
    flakes('__name__')


def test_magicGlobalsPath():
    """Use of the __path magic global should not emit an undefined name warning,

    if you refer to it from a file called __init__.py.

    """
    flakes('__path__', m.UndefinedName)
    flakes('__path__', filename='package/__init__.py')


def test_globalImportStar():
    """Can't find undefined names with import *."""
    flakes('from fu import *; bar', m.ImportStarUsed)


def test_localImportStar():
    """A local import * still allows undefined names to be found in upper scopes."""
    flakes('''
    def a():
        from fu import *
    bar
    ''', m.ImportStarUsed, m.UndefinedName)


@pytest.mark.skipif("version_info >= (3,)")
def test_unpackedParameter():
    """Unpacked function parameters create bindings."""
    flakes('''
    def a((bar, baz)):
        bar; baz
    ''')


@pytest.mark.skipif("'todo'")
def test_definedByGlobal():
    """"global" can make an otherwise undefined name in another function defined."""
    flakes('''
    def a(): global fu; fu = 1
    def b(): fu
    ''')


def test_globalInGlobalScope():
    """A global statement in the global scope is ignored."""
    flakes('''
    global x
    def foo():
        print(x)
    ''', m.UndefinedName)


def test_del():
    """Del deletes bindings."""
    flakes('a = 1; del a; a', m.UndefinedName)


def test_delGlobal():
    """Del a global binding from a function."""
    flakes('''
    a = 1
    def f():
        global a
        del a
    a
    ''')


def test_delUndefined():
    """Del an undefined name."""
    flakes('del a', m.UndefinedName)


def test_globalFromNestedScope():
    """Global names are available from nested scopes."""
    flakes('''
    a = 1
    def b():
        def c():
            a
    ''')


def test_laterRedefinedGlobalFromNestedScope():
    """Test that referencing a local name that shadows a global, before it is
    defined, generates a warning."""
    flakes('''
    a = 1
    def fun():
        a
        a = 2
        return a
    ''', m.UndefinedLocal)


def test_laterRedefinedGlobalFromNestedScope2():
    """Test that referencing a local name in a nested scope that shadows a
    global declared in an enclosing scope, before it is defined, generates a
    warning."""
    flakes('''
        a = 1
        def fun():
            global a
            def fun2():
                a
                a = 2
                return a
    ''', m.UndefinedLocal)


def test_intermediateClassScopeIgnored():
    """If a name defined in an enclosing scope is shadowed by a local variable
    and the name is used locally before it is bound, an unbound local warning
    is emitted, even if there is a class scope between the enclosing scope and
    the local scope."""
    flakes('''
    def f():
        x = 1
        class g:
            def h():
                a = x
                x = None
                print(x, a)
        print(x)
    ''', m.UndefinedLocal)


def test_doubleNestingReportsClosestName():
    """Test that referencing a local name in a nested scope that shadows a
    variable declared in two different outer scopes before it is defined in the
    innermost scope generates an UnboundLocal warning which refers to the
    nearest shadowed name."""
    exc = flakes('''
        def a():
            x = 1
            def b():
                x = 2 # line 5
                def c():
                    x
                    x = 3
                    return x
                return x
            return x
    ''', m.UndefinedLocal).messages[0]
    assert 'x' in exc.message
    assert str(5) in exc.message


def test_laterRedefinedGlobalFromNestedScope3():
    """Test that referencing a local name in a nested scope that shadows a
    global, before it is defined, generates a warning."""
    flakes('''
        def fun():
            a = 1
            def fun2():
                a
                a = 1
                return a
            return a
    ''', m.UndefinedLocal)


def test_undefinedAugmentedAssignment():
    flakes(
        '''
        def f(seq):
            a = 0
            seq[a] += 1
            seq[b] /= 2
            c[0] *= 2
            a -= 3
            d += 4
            e[any] = 5
        ''',
        m.UndefinedName,    # b
        m.UndefinedName,    # c
        m.UndefinedName, m.UnusedVariable,  # d
        m.UndefinedName,    # e
    )


def test_nestedClass():
    """Nested classes can access enclosing scope."""
    flakes('''
    def f(foo):
        class C:
            bar = foo
            def f():
                return foo
        return C()

    f(123).f()
    ''')


def test_badNestedClass():
    """Free variables in nested classes must bind at class creation."""
    flakes('''
    def f():
        class C:
            bar = foo
        foo = 456
        return foo
    f()
    ''', m.UndefinedName)


def test_definedAsStarArgs():
    """Star and double-star arg names are defined."""
    flakes('''
    def f(a, *b, **c):
        print(a, b, c)
    ''')


@pytest.mark.skipif("version_info < (3,)")
def test_definedAsStarUnpack():
    """Star names in unpack are defined."""
    flakes('''
    a, *b = range(10)
    print(a, b)
    ''')
    flakes('''
    *a, b = range(10)
    print(a, b)
    ''')
    flakes('''
    a, *b, c = range(10)
    print(a, b, c)
    ''')


@pytest.mark.skipif("version_info < (3,)")
def test_keywordOnlyArgs():
    """Keyword-only arg names are defined."""
    flakes('''
    def f(*, a, b=None):
        print(a, b)
    ''')

    flakes('''
    import default_b
    def f(*, a, b=default_b):
        print(a, b)
    ''')


@pytest.mark.skipif("version_info < (3,)")
def test_keywordOnlyArgsUndefined():
    """Typo in kwonly name."""
    flakes('''
    def f(*, a, b=default_c):
        print(a, b)
    ''', m.UndefinedName)


@pytest.mark.skipif("version_info < (3,)")
def test_annotationUndefined():
    """Undefined annotations."""
    flakes('''
    from abc import note1, note2, note3, note4, note5
    def func(a: note1, *args: note2,
                b: note3=12, **kw: note4) -> note5: pass
    ''')

    flakes('''
    def func():
        d = e = 42
        def func(a: {1, d}) -> (lambda c: e): pass
    ''')


@pytest.mark.skipif("version_info < (3,)")
def test_metaClassUndefined():
    flakes('''
    from abc import ABCMeta
    class A(metaclass=ABCMeta): pass
    ''')


def test_definedInGenExp():
    """Using the loop variable of a generator expression results in no
    warnings."""
    flakes('(a for a in %srange(10) if a)' %
                ('x' if version_info < (3,) else ''))


def test_undefinedWithErrorHandler():
    """Some compatibility code checks explicitly for NameError.

    It should not trigger warnings.

    """
    flakes('''
    try:
        socket_map
    except NameError:
        socket_map = {}
    ''')
    flakes('''
    try:
        _memoryview.contiguous
    except (NameError, AttributeError):
        raise RuntimeError("Python >= 3.3 is required")
    ''')
    # If NameError is not explicitly handled, generate a warning
    flakes('''
    try:
        socket_map
    except Exception:
        socket_map = {}
    ''', m.UndefinedName)
    flakes('''
    try:
        socket_map
    except Exception:
        socket_map = {}
    ''', m.UndefinedName)


def test_definedInClass():
    """Defined name for generator expressions and dict/set comprehension."""
    flakes('''
    class A:
        T = range(10)

        Z = (x for x in T)
        L = [x for x in T]
        B = dict((i, str(i)) for i in T)
    ''')

    if version_info >= (2, 7):
        flakes('''
        class A:
            T = range(10)

            X = {x for x in T}
            Y = {x:x for x in T}
        ''')


def test_impossibleContext():
    """A Name node with an unrecognized context results in a RuntimeError being raised."""
    tree = compile("x = 10", "<test>", "exec", PyCF_ONLY_AST)
    # Make it into something unrecognizable.
    tree.body[0].targets[0].ctx = object()
    with pytest.raises(RuntimeError):
        checker.Checker(tree)
