"""
    frosted/setup.py

    Defines how frosted should be installed on a standard Python system.

    Copyright (C) 2013  Timothy Edmund Crosley

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

try:
    from setuptools import setup
    extra = {
        'test_suite': 'frosted.test',
        'entry_points': {
            'console_scripts': ['frosted = frosted.api:main'],
        },
    }
except ImportError:
    from distutils.core import setup
    extra = {'scripts': ["bin/frosted"]}

setup(
    name="frosted",
    license="MIT",
    version="1.0.0",
    description="A passive Python syntax checker",
    author="Timothy Crosley",
    author_email="timothy.crosley@gmail.com",
    maintainer="Timothy Crosley",
    maintainer_email="timothy.crosley@gmail.com",
    url="https://github.com/timothycrosley/frosted",
    packages=["frosted", "frosted.scripts", "frosted.test"],
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
    **extra)
