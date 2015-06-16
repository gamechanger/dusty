import pwd
import subprocess
import textwrap
from os.path import isfile

from ..payload import Payload
from ..config import save_config_value, get_config_value, verify_mac_username, refresh_config_warnings
from ..log import log_to_client
from .. import constants
from .repos import update_managed_repos

def _pretty_print_key_info(config_key):
    print '{}: {}\n'.format(config_key, '\n'.join(textwrap.wrap(constants.CONFIG_SETTINGS[config_key], 80)))

def _get_raw_input(string):
    return raw_input(string).strip()

def _get_mac_username():
    _pretty_print_key_info(constants.CONFIG_MAC_USERNAME_KEY)
    proposed_mac_username = subprocess.check_output(['id', '-un']).strip()
    if _get_raw_input("Is {} the username under which you'll primarily use Dusty? (y/n): ".format(proposed_mac_username)).upper() == 'Y':
        return proposed_mac_username
    else:
        return _get_raw_input('Enter your actual mac_username: ')

def _get_default_specs_repo():
    _pretty_print_key_info(constants.CONFIG_SPECS_REPO_KEY)
    return _get_raw_input('Input the full name of your specs repo, e.g. github.com/gamechanger/example-dusty-specs: ')

def _get_nginx_includes_dir():
    nginx_includes_dir = None
    import logging
    for nginx_conf_location in constants.NGINX_CONFIG_FILE_LOCATIONS:
        file_location = '{}/nginx.conf'.format(nginx_conf_location)
        logging.error(file_location)
        if isfile(file_location):
            with open(file_location) as f:
                contents = f.read()
                logging.error(contents)
                if 'include servers/*;' in contents:
                    nginx_includes_dir = '{}/servers'.format(nginx_conf_location)
                    break

    if nginx_includes_dir is None:
        return _get_raw_input('You have non standard nginx config setup. Could not find an nginx.conf file that includes a directory. Please input the full path of the directory your nginx config includes. ')
    else:
        return nginx_includes_dir

def setup_dusty_config(mac_username=None, specs_repo=None, nginx_includes_dir=None):
    print "We just need to verify a few settings before we get started.\n"
    if mac_username:
        print 'Setting mac_username to {} based on flag'.format(mac_username)
    else:
        mac_username = _get_mac_username()
    verify_mac_username(mac_username)
    print ''

    if specs_repo:
        print 'Setting specs_repo to {} based on flag'.format(specs_repo)
    else:
        specs_repo = _get_default_specs_repo()
    print ''

    if nginx_includes_dir:
        print 'Setting nginx_includes_dir to {} based on flag'.format(nginx_includes_dir)
    else:
        nginx_includes_dir = _get_nginx_includes_dir()

    config_dictionary = {constants.CONFIG_MAC_USERNAME_KEY: mac_username,
                         constants.CONFIG_SPECS_REPO_KEY: specs_repo,
                         constants.CONFIG_NGINX_DIR_KEY: nginx_includes_dir}
    return Payload(complete_setup, config_dictionary)

def complete_setup(config):
    for key, value in config.iteritems():
        save_config_value(key, value)
    save_config_value(constants.CONFIG_SETUP_KEY, True)
    refresh_config_warnings()
    update_managed_repos()
    log_to_client('Initial setup completed. You should now be able to use Dusty!')
