from ..payload import Payload
from .. import constants
from ..config import save_config_value
from ..demote import check_output_demoted
from ..log import log_to_client

def _get_mac_username():
    proposed_mac_username = check_output_demoted(['echo', '$USER'])
    if input('Is {} your mac_username. Enter y for yes'.format(proposed_mac_username)).upper() == 'Y':
        return proposed_mac_username
    else:
        return input('Enter your actual mac_username: ').strip()

def _get_default_specs_repo():
    return input('Please input the repo of your specs repo. For example github.com/gamechanger/dusty: ').strip()

def _get_nginx_includes_dir():
    return input('Please input the path where your nginx config pulls extra configs.  The default value is: /usr/local/etc/nginx/servers').strip()

def setup_dusty_config():
    logging.info('Going to be setting values for these config values: {}'. constants.WARN_ON_MISSING_CONFIG_KEYS)
    mac_username = _get_mac_username()
    specs_repo = _get_default_specs_repo()
    nginx_includes_dir = _get_nginx_includes_dir()
    config_dictionary = {'mac_username': mac_username,
                         'specs_repo': specs_repo,
                         'nginx_includes_dir':nginx_includes_dir}

    return Payload(save_dusty_config, config_dictionary)


def save_dusty_config(dict):
    for key, value in dict.iteritems():
        save_config_value(key, value)
    save_config_value('setup_has_run', True)
    log_to_client('You should now be able to use dusty!')
