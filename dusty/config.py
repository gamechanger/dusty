"""Module for handling the user's config file stored at USER_CONFIG_PATH.
This file determines the bundles the user currently wants active, as well
as the location of the Dusty specifications on disk."""

import yaml

from .constants import USER_CONFIG_PATH

def _load(filepath):
    with open(filepath, 'r') as f:
        return yaml.load(f.read())

def _dump(doc):
    return yaml.dump(doc, default_flow_style=False)

def write_default_user_config():
    default_config = {'bundles': [], 'specs_path': '~/dusty-specs'}
    save_user_config(default_config)

def get_user_config():
    return _load(USER_CONFIG_PATH)

def save_user_config(config):
    with open(USER_CONFIG_PATH, 'w') as f:
        f.write(_dump(config))
