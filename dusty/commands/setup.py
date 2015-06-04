import pwd
import subprocess
import textwrap

from ..payload import Payload
from ..preflight import check_and_load_ssh_auth
from ..config import save_config_value, get_config_value
from ..log import log_to_client
from .. import constants

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

def _verify_mac_username(username):
    try:
        pwd.getpwnam(username)
    except:
        raise RuntimeError('No user found named {}'.format(username))

def _get_default_specs_repo():
    _pretty_print_key_info(constants.CONFIG_SPECS_REPO_KEY)
    return _get_raw_input('Input the full name of your specs repo, e.g. github.com/gamechanger/example-dusty-specs: ')

def _get_nginx_includes_dir():
    _pretty_print_key_info(constants.CONFIG_NGINX_DIR_KEY)
    default_nginx_config_value = get_config_value(constants.CONFIG_NGINX_DIR_KEY)
    if _get_raw_input('Does your nginx config look for extra configs in the default location of {}? (y/n): '.format(default_nginx_config_value)).upper() == 'Y':
        return default_nginx_config_value
    return _get_raw_input('Input the path where your nginx config pulls extra configs: ')

def setup_dusty_config(mac_username=None, specs_repo=None, nginx_includes_dir=None):
    print "We just need to verify a few settings before we get started.\n"
    if mac_username:
        print 'Setting mac_username to {} based on flag'.format(mac_username)
    else:
        mac_username = _get_mac_username()
    _verify_mac_username(mac_username)
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
    return Payload(save_dusty_config, config_dictionary)

def save_dusty_config(config):
    for key, value in config.iteritems():
        save_config_value(key, value)
    save_config_value(constants.CONFIG_SETUP_KEY, True)
    log_to_client('Initial setup completed. You should now be able to use Dusty!')
