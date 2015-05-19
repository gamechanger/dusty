from ..config import get_config, save_config_value

def list_config():
     yield get_config()

def save_value(key, value):
    config = get_config()
    if key not in config:
        yield 'key {} is not in config. Keep your config clean'.format(key)
    elif not isinstance(config[key], basestring):
        yield 'You can only modify string values in your config. {} has type {}'.format(key, type(config[key]))
    else:
        save_config_value(key, value)
        yield 'set {} to {} in your config'.format(key, value)

