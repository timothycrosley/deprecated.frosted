![frosted](https://raw.github.com/timothycrosley/frosted/master/logo.png)
=====

[![PyPI version](https://badge.fury.io/py/frosted.png)](http://badge.fury.io/py/frosted)
[![PyPi downloads](https://pypip.in/d/frosted/badge.png)](https://crate.io/packages/frosted/)
[![Build Status](https://travis-ci.org/timothycrosley/frosted.png?branch=master)](https://travis-ci.org/timothycrosley/frosted)
[![License](https://pypip.in/license/frosted/badge.png)](https://pypi.python.org/pypi/frosted/)
[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/timothycrosley/frosted/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

Frosted is a fork of pyflakes (originally created by Phil Frost) that aims at more open contribution from the outside public, a smaller more maintainable code base, and a better Python checker for all.
It currently cleanly supports Python 2.6 - 3.4 using pies (https://github.com/timothycrosley/pies) to achieve this without ugly hacks and/or py2to3.

Installing Frosted
===================

Installing Frosted is as simple as:

    pip install frosted --upgrade

or if you prefer

    easy_install frosted

Using Frosted
===================

**from the command line:**

    frosted mypythonfile.py mypythonfile2.py

or recursively:

    frosted -r .

 *which is equivalent to*

    frosted **/*.py

or to read from stdin:

    frosted -

**from within Python:**

    import frosted

    frosted.api.check_path("pythonfile.py")

Discussing improvements and getting help
===================

Using any of the following methods will result in a quick resolution to any issue you may have with Frosted
or a quick response to any implementation detail you wish to discuss.
  - [Mailing List](https://mail.python.org/mailman/listinfo/code-quality) - best place to discuss large architectural changes or changes that effect that may effect Python code-quality projects beyond Frosted.
  - [Github issues](https://github.com/timothycrosley/frosted/issues) - best place to report bugs, ask for concretely defined features, and even ask for general help.
  - <timothy.crosley@gmail.com> - feel free to email me any questions or concerns you have that you don't think would benefit from community wide involvement.

What makes Frosted better then pyflakes?
===================

The following improvements have already been implemented into Frosted

- Several improvements and fixes that have stayed open (and ignored) on mainline pyflakes have been integrated.
- Lots of code has been re-factored and simplified, Frosted aims to be faster and leaner then pyflakes ever was.
- Frosted adds the ability to configure which files you want to check, and which errors you don't care about. Which, in my opinion, is a must have feature.
- Frosted implements the .editorconfig standard for configuration. This means you only need one configuration file for isort, frosted, and all the code editors anybody working with your project may be using.
- Frosted uses a more logical, self-documenting, and standard terminal interface. With pyflakes the default action without any arguments is to do nothing (waiting for stdin) with Frosted you get an error and help.
- Frosted switched from Java style unittests to the more Pythonic py.test (I admit this is highly subjective).
- The number one reason frosted is better is because of you! Or rather, the Python community at large. I will quickly respond to any pull requests, recommendations, or bug reports that come my way.
- Frosting. Duh.

And it will only get better from here on out!

Configuring Frosted
======================

If you find the default frosted settings do not work well for your project, frosted provides several ways to adjust
the behavior.

To configure frosted for a single user create a ~/.frosted.cfg file:

    [settings]
    skip=file3.py,file4.py
    ignore_frosted_errors=E101,E205,E300
    run_doctests=True

- **skip** - A comma delimited list of file or directory names to skip. The name must exactly match the entire path, the name of the file, or one of it's parent directories for it to be skipped.
- **ignore_frosted_errors** - A comma delimited list of Frosted error codes to ignore. You can see a definition of all error codes in the next section.

Additionally, you can specify project level configuration simply by placing a .frosted.cfg file at the root of your
project. frosted will look up to 25 directories up, from the one it is ran, to find a project specific configuration.

You can then override any of these settings by using command line arguments, or by passing in kwargs into any of the
exposed api checking methods.

Beyond that, frosted supports setup.cfg based configuration. All you need to do is add a [frosted] section to your
project's setup.cfg file with any desired settings.

Finally, frosted supports editorconfig files using the standard syntax defined here:
http://editorconfig.org/

Meaning You can place any standard frosted configuration parameters within a .editorconfig file under the *.py section
and they will be honored.

Frosted Error Codes
======================

Frosted recognizes the following errors when present within your code. You can use the 'ignore_frosted_errors' setting to
specify any errors you want Frosted to ignore. If you specify the series error code (ex: E100) all errors in that series will be
ignored.

**I100 Series** - *General Information*
- **I101**: Generic

**E100 Series** - *Import Errors*
- **E101**: UnusedImport
    - Note that it is common practice to import something and not use it for the purpose of exposing it as an API, or using it in an exec statment below. Frosted tries to circumvent most of this by ignoring this error by default in __init__.py
- **E102**: ImportShadowedByLoopVar
- **E103**: ImportStarUsed

**E200 Series** - *Function / Method Definition and Calling Errors*
- **E201**: MultipleValuesForArgument
- **E202**: TooFewArguments
- **E203**: TooManyArguments
- **E204**: UnexpectedArgument
- **E205**: NeedKwOnlyArgument
- **E206**: DuplicateArgument
- **E207**: LateFutureImport
- **E208**: ReturnWithArgsInsideGenerator

**E300 Series** - *Variable / Definition Usage Errors*
- **E301**: RedefinedWhileUnused
- **E302**: RedefinedInListComp
- **E303**: UndefinedName
- **E304**: UndefinedExport
- **E305**: UndefinedLocal
- **E306**: Redefined
- **E307**: UnusedVariable

**E400 Series** - *Syntax Errors*
- **E401**: DoctestSyntaxError
- **E402**: PythonSyntaxError

**W100 Series** - *Exception Warning*
- **W101**: BareExcept
    - Note that one common case where a bare except is okay, and should be ignored is when handling the rollback of database transactions. In this or simular cases the warning can safely be ignored.

**W200 Series** - *Handling Warning*
- **W201**: FileSkipped


When deciding whether or not to include an error for reporting, Frosted uses the 99% approach as a yard stick. If it is agreed that 99% of the time (or more) that a pattern occurs it's an error, Frosted will report on it, if not it will not be added to the Frosted project.

Frosted Code API
===================

Frosted exposes a simple API for checking Python code from withing other Python applications or plugins.

- frosted.api.check (codeString, filename, reporter=modReporter.Default, **setting_overrides)
  Check the Python source given by codeString for unfrosted flakes.
- frosted.api.check_path (filename, reporter=modReporter.Default, **setting_overrides)
  Check the given path, printing out any warnings detected.
- frosted.check_recursive (paths, reporter=modReporter.Default, **setting_overrides)
  Recursively check all source files defined in paths.

Additionally, you can use the command line tool in an API fashion, by passing '-' in as the filename and then sending
file content to stdin.

Text Editor Integration
===================

Integration with text editors and tools is a priority for the project. As such, any pull request that adds integration support
or links to a third-party project that does will be enthusiastically accepted.

Current list of known supported text-editors:

- **vim** - Support has been added via syntastic: https://github.com/scrooloose/syntastic

Contributing to Frosted
===================

Our preferred contributions come in the form of pull requests and issue reports. That said, we will not deny monetary contributions.
If you desire to do this using flattr etc, please make sure you flattr @bitglue as he is the original creator of pyflakes and without his contribution
Frosted would not be possible.

Why did you fork pyflakes?
===================

Pyflakes was a great project, and introduced a great approach for quickly checking for Python coding errors. I am very grateful to the original creators.
However, I feel over the last year it has become stagnant, without a clear vision and someone willing to take true ownership of the project.
While I know it is in no way intentional, critical failures have stayed open, despite perfectly complete and valid pull-requests open, without so much as an acknowledgement from the maintainer.
As I genuinely believe open source projects need constant improvement (releasing early and often), I decided to start this project and look for as much
input as possible from the Python community. I'm hoping together we can build an even more awesome code checker!

Note: the maintainer of pyflakes has been added as a contributer to frosted.

Why Frosted?
===================

Frosted is a homage to the original pyflakes creator Phil Frost.

--------------------------------------------

Thanks and I hope you enjoy the new Frosted pyflakes!

~Timothy Crosley
