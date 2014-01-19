"""frosted/settings.py.

Defines how the default settings for frosted should be loaded

(First from the default setting dictionary at the top of the file, then overridden by any settings
 in ~/.frosted.conf if there are any)

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
from __future__ import absolute_import, division, print_function, unicode_literals

import os

from pies.overrides import *

MAX_CONFIG_SEARCH_DEPTH = 25 # The number of parent directories frosted will look for a config file within

# Note that none of these lists must be complete as they are simply fallbacks for when included auto-detection fails.
default = {'skip': ['__init__.py', ],
           'ignore_frosted_errors': [],
           'verbose': False}

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

editor_config_file = os.path.expanduser('~/.editorconfig')
tries = 0
current_directory = os.getcwd()
while current_directory and tries < MAX_CONFIG_SEARCH_DEPTH:
    potential_path = os.path.join(current_directory, ".editorconfig")
    if os.path.exists(potential_path):
        editor_config_file = potential_path
        break

    current_directory = os.path.split(current_directory)[0]
    tries += 1

if os.path.exists(editor_config_file):
    with open(editor_config_file) as config_file:
        line = "\n"
        last_position = config_file.tell()
        while line:
            line = config_file.readline()
            if "[" in line:
                config_file.seek(last_position)
                break
            last_position = config_file.tell()

        config = configparser.SafeConfigParser()
        config.readfp(config_file)
        settings = {}
        if config.has_section('*'):
            settings.update(dict(config.items('*')))
        if config.has_section('*.py'):
            settings.update(dict(config.items('*.py')))
        if config.has_section('**.py'):
            settings.update(dict(config.items('**.py')))

        for key, value in settings.items():
            existing_value_type = type(default.get(key, ''))
            if existing_value_type in (list, tuple):
                default[key.lower()] = value.split(",")
            else:
                default[key.lower()] = existing_value_type(value)

frosted_config_file = os.path.expanduser('~/.frosted.cfg')
tries = 0
current_directory = os.getcwd()
while current_directory and tries < MAX_CONFIG_SEARCH_DEPTH:
    potential_path = os.path.join(current_directory, ".frosted.cfg")
    if os.path.exists(potential_path):
        frosted_config_file = potential_path
        break

    current_directory = os.path.split(current_directory)[0]
    tries += 1

if os.path.exists(frosted_config_file):
    with open(frosted_config_file) as config_file:
        config = configparser.SafeConfigParser()
        config.readfp(config_file)
        settings = dict(config.items('settings'))
        for key, value in settings.items():
            existing_value_type = type(default.get(key, ''))
            if existing_value_type in (list, tuple):
                default[key.lower()] = value.split(",")
            else:
                default[key.lower()] = existing_value_type(value)
