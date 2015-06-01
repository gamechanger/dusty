"""Module for handling the daemon config file stored at CONFIG_PATH.
This file determines the bundles the user currently wants active, as well
as the location of the Dusty specifications on disk."""

import yaml

from . import constants
from .warnings import daemon_warnings

def _load(filepath):
    with open(filepath, 'r') as f:
        return yaml.load(f.read())

def _dump(doc):
    return yaml.dump(doc, default_flow_style=False)

def write_default_config():
    default_config = {'bundles': [], 'repo_overrides': {}}
    save_config(default_config)

def get_config():
    return _load(constants.CONFIG_PATH)

def save_config(config):
    with open(constants.CONFIG_PATH, 'w') as f:
        f.write(_dump(config))

def get_config_value(key):
    return get_config().get(key)

def save_config_value(key, value):
    current_config = get_config()
    current_config[key] = value
    save_config(current_config)

def refresh_config_warnings():
    daemon_warnings.clear_namespace('config')
    for key in sorted(constants.WARN_ON_MISSING_CONFIG_KEYS):
        if get_config_value(key) is None:
            daemon_warnings.warn('config',
                                 'Configuration key {} is not set, please set it using `dusty config`.'.format(key))

def assert_config_key(key):
    """Raises a KeyError if the given key is not currently present
    in the app config. It also ensures that keys with string values
    do not contain empty strings. Useful for enforcing that certain
    keys are present before entering codepaths that depend on them."""
    value = get_config_value(key)
    if value is None:
        raise KeyError('Configuration key {} is required'.format(key))
    elif isinstance(value, basestring) and value == '':
        raise KeyError('Configuration key {} cannot be an empty string'.format(key))
