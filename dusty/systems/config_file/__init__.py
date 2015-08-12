import logging
import re

from ... import constants


def read(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def write(filepath, contents):
    with open(filepath, 'w') as f:
        f.write(contents)

def remove_current_dusty_config(config):
    """Given a string representing the contents of a
    file, this function strips out the Dusty config section
    denominated by the Dusty header and footer. Returns
    the stripped string."""
    return constants.DUSTY_CONFIG_REGEX.sub("", config)

def create_config_section(contents):
    config = constants.DUSTY_CONFIG_BEGIN
    config += contents
    config += constants.DUSTY_CONFIG_END
    return config

def get_dusty_config_section(file_contents):
    m = constants.DUSTY_CONFIG_GROUP_REGEX.match(file_contents)
    if not m:
        return ''
    return m.group('dusty_config')

