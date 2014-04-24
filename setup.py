"""frosted/setup.py.

Defines how frosted should be installed on a standard Python system.

Copyright (C) 2005-2011 Divmod, Inc.
Copyright (C) 2013 Florent Xicluna. 
Copyright (C) 2014 Timothy Edmund Crosley

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
OTHER DEALINGS IN THE SOFTWARE.

"""

import os
import subprocess
import sys

try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand

    class PyTest(TestCommand):
        extra_kwargs = {'tests_require': ['pytest', 'mock']}

        def finalize_options(self):
            TestCommand.finalize_options(self)
            self.test_args = ['frosted/test']
            self.test_suite = True

        def run_tests(self):
            import pytest
            os.chdir
            sys.exit(pytest.main(self.test_args))

except ImportError:
    from distutils.core import setup, Command

    class PyTest(Command):
        extra_kwargs = {}
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            raise SystemExit(subprocess.call([sys.executable, 'runtests.py', 'frosted/test']))

try:
   import pypandoc
   readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError, RuntimeError):
   readme = ''

setup(name="frosted",
      license="MIT",
      version="1.4.1",
      description="A passive Python syntax checker",
      long_description=readme,
      author="Phil Frost",
      author_email="indigo@bitglue.com",
      maintainer="Timothy Crosley",
      maintainer_email="timothy.crosley@gmail.com",
      url="https://github.com/timothycrosley/frosted",
      packages=["frosted", "frosted.test"],
      requires=['pies'],
      install_requires=['pies>=2.6.0'],
      entry_points={
        'console_scripts': [
            'frosted = frosted.main:main',
        ]
      },
      cmdclass={'test': PyTest},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.0',
                   'Programming Language :: Python :: 3.1',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Topic :: Software Development',
                   'Topic :: Utilities'],
      **PyTest.extra_kwargs)
