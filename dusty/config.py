"""Module for handling the daemon config file stored at CONFIG_PATH.
This file determines the bundles the user currently wants active, as well
as the location of the Dusty specifications on disk."""

import logging
import os
import pwd
import subprocess
import yaml

from . import constants
from .warnings import daemon_warnings

def _load(filepath):
    with open(filepath, 'r') as f:
        return yaml.load(f.read())

def _dump(doc):
    return yaml.dump(doc, default_flow_style=False)

def write_default_config():
    default_config = {constants.CONFIG_BUNDLES_KEY: [],
                      constants.CONFIG_REPO_OVERRIDES_KEY: {},
                      constants.CONFIG_NGINX_DIR_KEY: '/usr/local/etc/nginx/servers',
                      constants.CONFIG_SETUP_KEY: False}
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
    if key == constants.CONFIG_MAC_USERNAME_KEY:
        verify_mac_username(value)
        save_config(current_config)
        check_and_load_ssh_auth()
    else:
        save_config(current_config)

def refresh_config_warnings():
    daemon_warnings.clear_namespace('config')
    for key in sorted(constants.WARN_ON_MISSING_CONFIG_KEYS):
        if get_config_value(key) is None:
            daemon_warnings.warn('config',
                                 'Configuration key {} is not set, please set it using `dusty config`.'.format(key))

def verify_mac_username(username):
    """Raise an error if the user doesn't exist"""
    try:
        pwd.getpwnam(username)
    except:
        raise RuntimeError('No user found named {}'.format(username))

def check_and_load_ssh_auth():
    """
    Will check the mac_username config value; if it is present, will load that user's
    SSH_AUTH_SOCK environment variable to the current environment.  This allows git clones
    to behave the same for the daemon as they do for the user
    """
    mac_username = get_config_value(constants.CONFIG_MAC_USERNAME_KEY)
    if not mac_username:
        logging.info("Can't setup ssh authorization; no mac_username specified")
    else:
        user_id = subprocess.check_output(['id', '-u', mac_username])
        _load_ssh_auth(user_id)

def _load_ssh_auth(user_id):
    ssh_auth_sock = subprocess.check_output(['launchctl', 'asuser', user_id, 'launchctl', 'getenv', 'SSH_AUTH_SOCK']).rstrip()
    if ssh_auth_sock:
        logging.info("Setting SSH_AUTH_SOCK to {}".format(ssh_auth_sock))
        os.environ['SSH_AUTH_SOCK'] = ssh_auth_sock
    else:
        daemon_warnings.warn('ssh', 'SSH_AUTH_SOCK not determined; git operations may fail')
