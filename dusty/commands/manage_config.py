import textwrap

from prettytable import PrettyTable

from ..config import get_config, save_config_value
from .. import constants

def _eligible_config_keys_for_setting():
     config = get_config()
     return [key for key in sorted(constants.CONFIG_SETTINGS.keys())
             if key not in config or isinstance(config[key], basestring)]

def list_config():
     config = get_config()
     table = PrettyTable(['Key', 'Description', 'Value'])
     for key, description in constants.CONFIG_SETTINGS.iteritems():
          table.add_row([key, '\n'.join(textwrap.wrap(description, 80)), config.get(key)])
     yield table.get_string(sortby='Key')

def list_config_values():
     yield get_config()

def save_value(key=None, value=None):
    if key is None and value is None:
        yield 'Call with arguments `key value`, where key is in {}'.format(_eligible_config_keys_for_setting())
        return
    elif value is None:
        raise ValueError('Value cannot be None')
    config = get_config()
    if key not in constants.CONFIG_SETTINGS:
        raise KeyError('Your key {} must be in the list {}'.format(key, sorted(constants.CONFIG_SETTINGS.keys())))
    if key in config and not isinstance(config[key], basestring):
        raise KeyError('You can only modify string values in your config. {} has type {}'.format(key, type(config[key])))
    else:
        save_config_value(key, value)
        yield 'Set {} to {} in your config'.format(key, value)
