import subprocess

from ..payload import Payload
from ..config import save_config_value, get_config_value
from ..log import log_to_client

def _get_raw_input(string):
    return raw_input(string).strip()

def _get_mac_username():
    proposed_mac_username = subprocess.check_output(['id', '-un']).strip()
    if _get_raw_input('Is {} your mac_username. y or no: '.format(proposed_mac_username)).upper() == 'Y':
        return proposed_mac_username
    else:
        return _get_raw_input('Enter your actual mac_username: ')

def _get_default_specs_repo():
    return _get_raw_input('Please input the name your specs repo. For example github.com/gamechanger/dusty: ')

def _get_nginx_includes_dir():
    default_nginx_config_value = get_config_value('nginx_includes_dir')
    if _get_raw_input('Does your nginx config look for extra configs in the default location of {}. y or n: '.format(default_nginx_config_value)).upper() == 'Y':
        return default_nginx_config_value
    return _get_raw_input('Please input the path where your nginx config pulls extra configs: ')

def setup_dusty_config(mac_username=None, specs_repo=None, nginx_includes_dir=None):
    mac_username = _get_mac_username() if mac_username is None else mac_username
    specs_repo = _get_default_specs_repo() if specs_repo is None else specs_repo
    nginx_includes_dir = _get_nginx_includes_dir() if nginx_includes_dir is None else nginx_includes_dir
    config_dictionary = {'mac_username': mac_username,
                         'specs_repo': specs_repo,
                         'nginx_includes_dir':nginx_includes_dir}

    return Payload(save_dusty_config, config_dictionary)


def save_dusty_config(dict):
    for key, value in dict.iteritems():
        save_config_value(key, value)
    save_config_value('setup_has_run', True)
    log_to_client('You should now be able to use dusty!')
