![frosted](https://raw.github.com/timothycrosley/frosted/master/logo.png)
=====

[![PyPI version](https://badge.fury.io/py/frosted.png)](http://badge.fury.io/py/frosted)
[![PyPi downloads](https://pypip.in/d/frosted/badge.png)](https://crate.io/packages/frosted/)
[![Build Status](https://travis-ci.org/timothycrosley/frosted.png?branch=master)](https://travis-ci.org/timothycrosley/frosted)
[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/timothycrosley/frosted/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

Frosted is a fork of pyflakes that aims at more open contribution from the outside public, a smaller more maintainable code base, and a better Python checker for all.
It currently cleanly supports Python 2.6 - 3.4 using pies (https://github.com/timothycrosley/pies) to achieve this without ugly hacks and/or py2to3.

Installing Frosted
===================

Installing Frosted is as simple as:

    pip install frosted --upgrade

or if you prefer

    easy_install frosted

Using Frosted
===================

from the command line:

    frosted mypythonfile.py mypythonfile2.py

or recursively:

    frosted -r .

 *which is equivalent to*

    frosted **/*.py

or to read from stdin:

    frosted -

from within Python:

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


Additionally, you can specify project level configuration simply by placing a .frosted.cfg file at the root of your
project. frosted will look up to 25 directories up, from the one it is ran, to find a project specific configuration.

You can then override any of these settings by using command line arguments, or by passing in kwargs into any of the
exposed api checking methods.

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

**W100 Series** - *Exception Warning*
- **W101**: BareExcept

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

Why did you fork pyflakes?
===================

Pyflakes was a great project, and introduced a great approach for quickly checking for Python coding errors. I am very grateful to the original creators.
However, I feel over the last year it has become stagnate, without a clear vision and someone willing to take true ownership of the project.
While I know it is in no way intentional, critical failures have stayed open, despite perfectly complete and valid pull-requests open, without so much as an acknowledgement from the maintainer.
As I genuinely believe open source projects need constant improvement (releasing early and often), I decided to start this project and look for as much
input as possible from the Python community. I'm hoping together we can build an even more awesome code checker!

Note: the maintainer of pyflakes has been added as a contributer to frosted.

--------------------------------------------

Thanks and I hope you enjoy the new Frosted pyflakes!

~Timothy Crosley
