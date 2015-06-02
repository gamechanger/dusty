from ..payload import Payload
from .. import constants
from ..config import save_config_dict

def _get_mac_username():

def _get_default_specs_repo():

def _get_nginx_includes_dir():


def setup_dusty_config():
    logging.info('Going to be setting values for these config values: {}'. constants.WARN_ON_MISSING_CONFIG_KEYS)
    mac_username = _get_mac_username()
    specs_repo = _get_default_specs_repo()
    nginx_includes_dir = _get_nginx_includes_dir()
    config_dictionary = {'mac_username': mac_username,
                         'specs_repo': specs_repo,
                         'nginx_includes_dir':nginx_includes_dir}

    return Payload(save_config_dict, config_dictionary)
