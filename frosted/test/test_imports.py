
from __future__ import absolute_import, division, print_function, unicode_literals

from sys import version_info

import pytest
from pies.overrides import *

from frosted import messages as m

from .utils import flakes


def test_unusedImport():
    flakes('import fu, bar', m.UnusedImport, m.UnusedImport)
    flakes('from baz import fu, bar', m.UnusedImport, m.UnusedImport)


def test_aliasedImport():
    flakes('import fu as FU, bar as FU',
                m.RedefinedWhileUnused, m.UnusedImport)
    flakes('from moo import fu as FU, bar as FU',
                m.RedefinedWhileUnused, m.UnusedImport)


def test_usedImport():
    flakes('import fu; print(fu)')
    flakes('from baz import fu; print(fu)')
    flakes('import fu; del fu')


def test_redefinedWhileUnused():
    flakes('import fu; fu = 3', m.RedefinedWhileUnused)
    flakes('import fu; fu, bar = 3', m.RedefinedWhileUnused)
    flakes('import fu; [fu, bar] = 3', m.RedefinedWhileUnused)


def test_redefinedIf():
    """Test that importing a module twice within an if block does raise a warning."""
    flakes('''
    i = 2
    if i==1:
        import os
        import os
    os.path''', m.RedefinedWhileUnused)


def test_redefinedIfElse():
    """Test that importing a module twice in if and else blocks does not raise a warning."""
    flakes('''
    i = 2
    if i==1:
        import os
    else:
        import os
    os.path''')


def test_redefinedTry():
    """Test that importing a module twice in an try block does raise a warning."""
    flakes('''
    try:
        import os
        import os
    except Exception:
        pass
    os.path''', m.RedefinedWhileUnused)


def test_redefinedTryExcept():
    """Test that importing a module twice in an try and except block does not raise a warning."""
    flakes('''
    try:
        import os
    except Exception:
        import os
    os.path''')


def test_redefinedTryNested():
    """Test that importing a module twice using a nested try/except and if blocks does not issue a warning."""
    flakes('''
    try:
        if True:
            if True:
                import os
    except Exception:
        import os
    os.path''')


def test_redefinedTryExceptMulti():
    flakes("""
    try:
        from aa import mixer
    except AttributeError:
        from bb import mixer
    except RuntimeError:
        from cc import mixer
    except Exception:
        from dd import mixer
    mixer(123)
    """)


def test_redefinedTryElse():
    flakes("""
    try:
        from aa import mixer
    except ImportError:
        pass
    else:
        from bb import mixer
    mixer(123)
    """, m.RedefinedWhileUnused)


def test_redefinedTryExceptElse():
    flakes("""
    try:
        import funca
    except ImportError:
        from bb import funca
        from bb import funcb
    else:
        from bbb import funcb
    print(funca, funcb)
    """)


def test_redefinedTryExceptFinally():
    flakes("""
    try:
        from aa import a
    except ImportError:
        from bb import a
    finally:
        a = 42
    print(a)
    """)


def test_redefinedTryExceptElseFinally():
    flakes("""
    try:
        import b
    except ImportError:
        b = Ellipsis
        from bb import a
    else:
        from aa import a
    finally:
        a = 42
    print(a, b)
    """)


def test_redefinedByFunction():
    flakes('''
    import fu
    def fu():
        pass
    ''', m.RedefinedWhileUnused)


def test_redefinedInNestedFunction():
    """Test that shadowing a global name with a nested function definition generates a warning."""
    flakes('''
    import fu
    def bar():
        def baz():
            def fu():
                pass
    ''', m.RedefinedWhileUnused, m.UnusedImport)


def test_redefinedByClass():
    flakes('''
    import fu
    class fu:
        pass
    ''', m.RedefinedWhileUnused)


def test_redefinedBySubclass():
    """If an imported name is redefined by a class statement

    which also uses that name in the bases list, no warning is emitted.

    """
    flakes('''
    from fu import bar
    class bar(bar):
        pass
    ''')


def test_redefinedInClass():
    """Test that shadowing a global with a class attribute does not produce a warning."""
    flakes('''
    import fu
    class bar:
        fu = 1
    print(fu)
    ''')


def test_usedInFunction():
    flakes('''
    import fu
    def fun():
        print(fu)
    ''')


def test_shadowedByParameter():
    flakes('''
    import fu
    def fun(fu):
        print(fu)
    ''', m.UnusedImport)

    flakes('''
    import fu
    def fun(fu):
        print(fu)
    print(fu)
    ''')


def test_newAssignment():
    flakes('fu = None')


def test_usedInGetattr():
    flakes('import fu; fu.bar.baz')
    flakes('import fu; "bar".fu.baz', m.UnusedImport)


def test_usedInSlice():
    flakes('import fu; print(fu.bar[1:])')


def test_usedInIfBody():
    flakes('''
    import fu
    if True: print(fu)
    ''')


def test_usedInIfConditional():
    flakes('''
    import fu
    if fu: pass
    ''')


def test_usedInElifConditional():
    flakes('''
    import fu
    if False: pass
    elif fu: pass
    ''')


def test_usedInElse():
    flakes('''
    import fu
    if False: pass
    else: print(fu)
    ''')


def test_usedInCall():
    flakes('import fu; fu.bar()')


def test_usedInClass():
    flakes('''
    import fu
    class bar:
        bar = fu
    ''')


def test_usedInClassBase():
    flakes('''
    import fu
    class bar(object, fu.baz):
        pass
    ''')


def test_notUsedInNestedScope():
    flakes('''
    import fu
    def bleh():
        pass
    print(fu)
    ''')


def test_usedInFor():
    flakes('''
    import fu
    for bar in range(9):
        print(fu)
    ''')


def test_usedInForElse():
    flakes('''
    import fu
    for bar in range(10):
        pass
    else:
        print(fu)
    ''')


def test_redefinedByFor():
    flakes('''
    import fu
    for fu in range(2):
        pass
    ''', m.RedefinedWhileUnused)


def test_shadowedByFor():
    """Test that shadowing a global name with a for loop variable generates a warning."""
    flakes('''
    import fu
    fu.bar()
    for fu in ():
        pass
    ''', m.ImportShadowedByLoopVar)


def test_shadowedByForDeep():
    """Test that shadowing a global name with a for loop variable nested in a tuple unpack generates a warning."""
    flakes('''
    import fu
    fu.bar()
    for (x, y, z, (a, b, c, (fu,))) in ():
        pass
    ''', m.ImportShadowedByLoopVar)


def test_usedInReturn():
    flakes('''
    import fu
    def fun():
        return fu
    ''')


def test_usedInOperators():
    flakes('import fu; 3 + fu.bar')
    flakes('import fu; 3 % fu.bar')
    flakes('import fu; 3 - fu.bar')
    flakes('import fu; 3 * fu.bar')
    flakes('import fu; 3 ** fu.bar')
    flakes('import fu; 3 / fu.bar')
    flakes('import fu; 3 // fu.bar')
    flakes('import fu; -fu.bar')
    flakes('import fu; ~fu.bar')
    flakes('import fu; 1 == fu.bar')
    flakes('import fu; 1 | fu.bar')
    flakes('import fu; 1 & fu.bar')
    flakes('import fu; 1 ^ fu.bar')
    flakes('import fu; 1 >> fu.bar')
    flakes('import fu; 1 << fu.bar')


def test_usedInAssert():
    flakes('import fu; assert fu.bar')


def test_usedInSubscript():
    flakes('import fu; fu.bar[1]')


def test_usedInLogic():
    flakes('import fu; fu and False')
    flakes('import fu; fu or False')
    flakes('import fu; not fu.bar')


def test_usedInList():
    flakes('import fu; [fu]')


def test_usedInTuple():
    flakes('import fu; (fu,)')


def test_usedInTry():
    flakes('''
    import fu
    try: fu
    except Exception: pass
    ''')


def test_usedInExcept():
    flakes('''
    import fu
    try: fu
    except Exception: pass
    ''')


def test_redefinedByExcept():
    as_exc = ', ' if version_info < (2, 6) else ' as '
    flakes('''
    import fu
    try: pass
    except Exception%sfu: pass
    ''' % as_exc, m.RedefinedWhileUnused)


def test_usedInRaise():
    flakes('''
    import fu
    raise fu.bar
    ''')


def test_usedInYield():
    flakes('''
    import fu
    def gen():
        yield fu
    ''')


def test_usedInDict():
    flakes('import fu; {fu:None}')
    flakes('import fu; {1:fu}')


def test_usedInParameterDefault():
    flakes('''
    import fu
    def f(bar=fu):
        pass
    ''')


def test_usedInAttributeAssign():
    flakes('import fu; fu.bar = 1')


def test_usedInKeywordArg():
    flakes('import fu; fu.bar(stuff=fu)')


def test_usedInAssignment():
    flakes('import fu; bar=fu')
    flakes('import fu; n=0; n+=fu')


def test_usedInListComp():
    flakes('import fu; [fu for _ in range(1)]')
    flakes('import fu; [1 for _ in range(1) if fu]')


def test_redefinedByListComp():
    flakes('import fu; [1 for fu in range(1)]', m.RedefinedWhileUnused)


def test_usedInTryFinally():
    flakes('''
    import fu
    try: pass
    finally: fu
    ''')

    flakes('''
    import fu
    try: fu
    finally: pass
    ''')


def test_usedInWhile():
    flakes('''
    import fu
    while 0:
        fu
    ''')

    flakes('''
    import fu
    while fu: pass
    ''')


def test_usedInGlobal():
    flakes('''
    import fu
    def f(): global fu
    ''', m.UnusedImport)


@pytest.mark.skipif("version_info >= (3,)")
def test_usedInBackquote():
    flakes('import fu; `fu`')


def test_usedInExec():
    if version_info < (3,):
        exec_stmt = 'exec "print 1" in fu.bar'
    else:
        exec_stmt = 'exec("print(1)", fu.bar)'
    flakes('import fu; %s' % exec_stmt)


def test_usedInLambda():
    flakes('import fu; lambda: fu')


def test_shadowedByLambda():
    flakes('import fu; lambda fu: fu', m.UnusedImport)


def test_usedInSliceObj():
    flakes('import fu; "meow"[::fu]')


def test_unusedInNestedScope():
    flakes('''
    def bar():
        import fu
    fu
    ''', m.UnusedImport, m.UndefinedName)


def test_methodsDontUseClassScope():
    flakes('''
    class bar:
        import fu
        def fun():
            fu
    ''', m.UnusedImport, m.UndefinedName)


def test_nestedFunctionsNestScope():
    flakes('''
    def a():
        def b():
            fu
        import fu
    ''')


def test_nestedClassAndFunctionScope():
    flakes('''
    def a():
        import fu
        class b:
            def c():
                print(fu)
    ''')


def test_importStar():
    flakes('from fu import *', m.ImportStarUsed, ignore_frosted_errors=[])


def test_packageImport():
    """If a dotted name is imported and used, no warning is reported."""
    flakes('''
    import fu.bar
    fu.bar
    ''')


def test_unusedPackageImport():
    """If a dotted name is imported and not used, an unused import warning is reported."""
    flakes('import fu.bar', m.UnusedImport)


def test_duplicateSubmoduleImport():
    """If a submodule of a package is imported twice, an unused

    import warning and a redefined while unused warning are reported.

    """
    flakes('''
    import fu.bar, fu.bar
    fu.bar
    ''', m.RedefinedWhileUnused)
    flakes('''
    import fu.bar
    import fu.bar
    fu.bar
    ''', m.RedefinedWhileUnused)


def test_differentSubmoduleImport():
    """If two different submodules of a package are imported,

    no duplicate import warning is reported for the package.

    """
    flakes('''
    import fu.bar, fu.baz
    fu.bar, fu.baz
    ''')
    flakes('''
    import fu.bar
    import fu.baz
    fu.bar, fu.baz
    ''')


def test_assignRHSFirst():
    flakes('import fu; fu = fu')
    flakes('import fu; fu, bar = fu')
    flakes('import fu; [fu, bar] = fu')
    flakes('import fu; fu += fu')


def test_tryingMultipleImports():
    flakes('''
    try:
        import fu
    except ImportError:
        import bar as fu
    fu
    ''')


def test_nonGlobalDoesNotRedefine():
    flakes('''
    import fu
    def a():
        fu = 3
        return fu
    fu
    ''')


def test_functionsRunLater():
    flakes('''
    def a():
        fu
    import fu
    ''')


def test_functionNamesAreBoundNow():
    flakes('''
    import fu
    def fu():
        fu
    fu
    ''', m.RedefinedWhileUnused)


def test_ignoreNonImportRedefinitions():
    flakes('a = 1; a = 2')


@pytest.mark.skipif("'todo'")
def test_importingForImportError():
    flakes('''
    try:
        import fu
    except ImportError:
        pass
    ''')


@pytest.mark.skipif("'todo: requires evaluating attribute access'")
def test_importedInClass():
    """Imports in class scope can be used through."""
    flakes('''
    class c:
        import i
        def __init__():
            i
    ''')


def test_futureImport():
    """__future__ is special."""
    flakes('from __future__ import division')
    flakes('''
    "docstring is allowed before future import"
    from __future__ import division
    ''')


def test_futureImportFirst():
    """__future__ imports must come before anything else."""
    flakes('''
    x = 5
    from __future__ import division
    ''', m.LateFutureImport)
    flakes('''
    from foo import bar
    from __future__ import division
    bar
    ''', m.LateFutureImport)


def test_ignoredInFunction():
    """An C{__all__} definition does not suppress unused import warnings in a function scope."""
    flakes('''
    def foo():
        import bar
        __all__ = ["bar"]
    ''', m.UnusedImport, m.UnusedVariable)


def test_ignoredInClass():
    """An C{__all__} definition does not suppress unused import warnings in a class scope."""
    flakes('''
    class foo:
        import bar
        __all__ = ["bar"]
    ''', m.UnusedImport)


def test_warningSuppressed():
    """If a name is imported and unused but is named in C{__all__}, no warning is reported."""
    flakes('''
    import foo
    __all__ = ["foo"]
    ''')


def test_unrecognizable():
    """If C{__all__} is defined in a way that can't be recognized statically, it is ignored."""
    flakes('''
    import foo
    __all__ = ["f" + "oo"]
    ''', m.UnusedImport)
    flakes('''
    import foo
    __all__ = [] + ["foo"]
    ''', m.UnusedImport)


def test_unboundExported():
    """If C{__all__} includes a name which is not bound, a warning is emitted."""
    flakes('''
    __all__ = ["foo"]
    ''', m.UndefinedExport)

    # Skip this in __init__.py though, since the rules there are a little
    # different.
    for filename in ["foo/__init__.py", "__init__.py"]:
        flakes('''
        __all__ = ["foo"]
        ''', filename=filename, **{'ignore_frosted_errors_for___init__.py': ['E101', 'E103']})


def test_importStarExported():
    """Do not report undefined if import * is used"""
    flakes('''
    from foolib import *
    __all__ = ["foo"]
    ''', m.ImportStarUsed)


def test_usedInGenExp():
    """Using a global in a generator expression results in no warnings."""
    flakes('import fu; (fu for _ in range(1))')
    flakes('import fu; (1 for _ in range(1) if fu)')


def test_redefinedByGenExp():
    """ Re-using a global name as the loop variable for a generator

    expression results in a redefinition warning.

    """
    flakes('import fu; (1 for fu in range(1))', m.RedefinedWhileUnused, m.UnusedImport)


def test_usedAsDecorator():
    """Using a global name in a decorator statement results in no warnings, but

    using an undefined name in a decorator statement results in an undefined
    name warning.

    """
    flakes('''
    from interior import decorate
    @decorate
    def f():
        return "hello"
    ''')

    flakes('''
    from interior import decorate
    @decorate('value')
    def f():
        return "hello"
    ''')

    flakes('''
    @decorate
    def f():
        return "hello"
    ''', m.UndefinedName)


def test_usedAsClassDecorator():
    """Using an imported name as a class decorator results in no warnings

    but using an undefined name as a class decorator results in an undefined name warning.

    """
    flakes('''
    from interior import decorate
    @decorate
    class foo:
        pass
    ''')

    flakes('''
    from interior import decorate
    @decorate("foo")
    class bar:
        pass
    ''')

    flakes('''
    @decorate
    class foo:
        pass
    ''', m.UndefinedName)
