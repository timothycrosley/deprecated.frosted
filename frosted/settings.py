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

from pies.functools import lru_cache
from pies.overrides import *

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

MAX_CONFIG_SEARCH_DEPTH = 25 # The number of parent directories frosted will look for a config file within

# Note that none of these lists must be complete as they are simply fallbacks for when included auto-detection fails.
default = {'skip': [],
           'ignore_frosted_errors': ['W201'],
           'ignore_frosted_errors_for__init__.py': ['E101', 'E103'],
           'verbose': False,
           'run_doctests': False}


@lru_cache()
def from_path(path):
    computed_settings = default.copy()
    _update_settings_with_config(path, '.editorconfig', '~/.editorconfig', ('*', '*.py', '**.py'), computed_settings)
    _update_settings_with_config(path, '.frosted.cfg', '~/.frosted.cfg', ('settings', ), computed_settings)
    _update_settings_with_config(path, 'setup.cfg', None, ('frosted', ), computed_settings)
    return computed_settings


def _update_settings_with_config(path, name, default, sections, computed_settings):
    editor_config_file = default and os.path.expanduser(default)
    tries = 0
    current_directory = path
    while current_directory and tries < MAX_CONFIG_SEARCH_DEPTH:
        potential_path = os.path.join(current_directory, native_str(name))
        if os.path.exists(potential_path):
            editor_config_file = potential_path
            break

        current_directory = os.path.split(current_directory)[0]
        tries += 1

    if editor_config_file and os.path.exists(editor_config_file):
        _update_with_config_file(computed_settings, editor_config_file, sections)


def _update_with_config_file(computed_settings, file_path, sections):
    settings = _get_config_data(file_path, sections)
    if not settings:
        return

    for key, value in settings.items():
        access_key = key.replace('not_', '').lower()
        if key.startswith('ignore_frosted_errors_for'):
            existing_value_type = list
        else:
            existing_value_type = type(default.get(access_key, ''))
        if existing_value_type in (list, tuple):
            existing_data = set(computed_settings.get(access_key, default.get(access_key)) or ())
            if key.startswith('not_'):
                computed_settings[access_key] = list(existing_data.difference(value.split(",")))
            else:
                computed_settings[access_key] = list(existing_data.union(value.split(",")))
        elif existing_value_type == bool and value.lower().strip() == "false":
            computed_settings[access_key] = False
        else:
            computed_settings[access_key] = existing_value_type(value)


@lru_cache()
def _get_config_data(file_path, sections):
    with open(file_path) as config_file:
        if file_path.endswith(".editorconfig"):
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
        settings = dict()
        for section in sections:
            if config.has_section(section):
                settings.update(dict(config.items(section)))

        return settings

    return None
