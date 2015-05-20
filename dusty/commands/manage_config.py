from ..config import get_config, save_config_value
from .. import constants

def _eligible_config_keys_for_setting():
     config = get_config()
     return [key for key in constants.CONFIG_KEY_WHITELIST
             if key not in config or isinstance(config[key], basestring)]

def list_config():
     yield get_config()

def save_value(key=None, value=None):
    if key is None and value is None:
        yield 'Call with arguments `key value`, where key is in {}'.format(_eligible_config_keys_for_setting())
        return
    elif value is None:
        raise ValueError('Value cannot be None')
    config = get_config()
    if key not in constants.CONFIG_KEY_WHITELIST:
        raise KeyError('Your key {} must be in the list {}'.format(key, constants.CONFIG_KEY_WHITELIST))
    if key in config and not isinstance(config[key], basestring):
        raise KeyError('You can only modify string values in your config. {} has type {}'.format(key, type(config[key])))
    else:
        save_config_value(key, value)
        yield 'Set {} to {} in your config'.format(key, value)
