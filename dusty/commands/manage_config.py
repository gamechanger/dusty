from ..config import get_config, save_config_value
from ..constants import CONFIG_KEY_WHITE_LIST

def list_config():
     yield get_config()

def save_value(key, value):
    config = get_config()
    if key not in CONFIG_KEY_WHITE_LIST:
        raise KeyError('Your key {} must be in the list {}'.format(key, CONFIG_KEY_WHITE_LIST))
    if key in config and not isinstance(config[key], basestring):
        raise KeyError('You can only modify string values in your config. {} has type {}'.format(key, type(config[key])))
    else:
        save_config_value(key, value)
        yield 'set {} to {} in your config'.format(key, value)

