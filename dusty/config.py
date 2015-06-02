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
    default_config = {'bundles': [],
                      'repo_overrides': {},
                      'nginx_includes_dir': '/usr/local/etc/nginx/servers'}
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

def save_config_dict(dict):
    for key, value in dict.iteritems():
        save_config_value(key, value)

def refresh_config_warnings():
    daemon_warnings.clear_namespace('config')
    for key in sorted(constants.WARN_ON_MISSING_CONFIG_KEYS):
        if get_config_value(key) is None:
            daemon_warnings.warn('config',
                                 'Configuration key {} is not set, please set it using `dusty config`.'.format(key))
