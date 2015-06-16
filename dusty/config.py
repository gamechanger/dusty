"""Module for handling the daemon config file stored at CONFIG_PATH.
This file determines the bundles the user currently wants active, as well
as the location of the Dusty specifications on disk."""

from __future__ import absolute_import

import os
import logging
import pwd
import subprocess
import yaml
import platform

import psutil

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

def _running_on_mac():
    return bool(platform.mac_ver()[0])

def _mac_version_is_post_yosemite():
    version = platform.mac_ver()[0]
    minor_version = int(version.split('.')[1])
    return minor_version >= 10

def _load_ssh_auth_post_yosemite(mac_username):
    """Starting with Yosemite, launchd was rearchitected and now only one
    launchd process runs for all users. This allows us to much more easily
    impersonate a user through launchd and extract the environment
    variables from their running processes."""
    user_id = subprocess.check_output(['id', '-u', mac_username])
    ssh_auth_sock = subprocess.check_output(['launchctl', 'asuser', user_id, 'launchctl', 'getenv', 'SSH_AUTH_SOCK']).rstrip()
    _set_ssh_auth_sock(ssh_auth_sock)

def _load_ssh_auth_pre_yosemite():
    """For OS X versions before Yosemite, many launchd processes run simultaneously under
    different users and different permission models. The simpler `asuser` trick we use
    in Yosemite doesn't work, since it gets routed to the wrong launchd. We instead need
    to find the running ssh-agent process and use its PID to navigate ourselves
    to the correct launchd."""
    for process in psutil.process_iter():
        if process.name() == 'ssh-agent':
            ssh_auth_sock = subprocess.check_output(['launchctl', 'bsexec', str(process.pid), 'launchctl', 'getenv', 'SSH_AUTH_SOCK']).rstrip()
            if ssh_auth_sock:
                _set_ssh_auth_sock(ssh_auth_sock)
                break
    else:
        daemon_warnings.warn('ssh', 'No running ssh-agent found linked to SSH_AUTH_SOCK')

def _set_ssh_auth_sock(ssh_auth_sock):
    if ssh_auth_sock:
        logging.info("Setting SSH_AUTH_SOCK to {}".format(ssh_auth_sock))
        os.environ['SSH_AUTH_SOCK'] = ssh_auth_sock
    else:
        daemon_warnings.warn('ssh', 'SSH_AUTH_SOCK not determined; git operations may fail')

def check_and_load_ssh_auth():
    """
    Will check the mac_username config value; if it is present, will load that user's
    SSH_AUTH_SOCK environment variable to the current environment.  This allows git clones
    to behave the same for the daemon as they do for the user
    """
    if os.getenv('SSH_AUTH_SOCK'):
        logging.info('SSH_AUTH_SOCK already set')
        return _set_ssh_auth_sock(os.getenv('SSH_AUTH_SOCK'))

    mac_username = get_config_value(constants.CONFIG_MAC_USERNAME_KEY)
    if not mac_username:
        logging.info("Can't setup ssh authorization; no mac_username specified")
        return
    if not _running_on_mac(): # give our Linux unit tests a way to not freak out
        logging.info("Skipping SSH load, we are not running on Mac")
        return

    if _mac_version_is_post_yosemite():
        _load_ssh_auth_post_yosemite(mac_username)
    else:
        _load_ssh_auth_pre_yosemite()
