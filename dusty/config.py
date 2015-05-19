"""Module for handling the daemon config file stored at CONFIG_PATH.
This file determines the bundles the user currently wants active, as well
as the location of the Dusty specifications on disk."""

import yaml

from . import constants

def _load(filepath):
    with open(filepath, 'r') as f:
        return yaml.load(f.read())

def _dump(doc):
    return yaml.dump(doc, default_flow_style=False)

def write_default_config():
    default_config = {'bundles': [], 'specs_path': '~/dusty-specs', 'repo_overrides': {}}
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

def assert_config_key(key, empty_value=None):
    """Raises a KeyError if the given key is not currently present
    in the app config. Useful for enforcing that certain keys are
    present before entering codepaths that depend on them."""
    value = get_config_value(key)
    if value is None:
        raise KeyError('Configuration key {} is required'.format(key))
    elif empty_value is not None and value == empty_value:
        raise KeyError('Configuration key {} cannot have empty value of {}'.format(key, empty_value))
