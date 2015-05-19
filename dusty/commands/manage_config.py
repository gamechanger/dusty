from ..config import get_config, save_config

def list_config():
     yield str(get_config())

def set_value(key, value):
    config = get_config()
    if key not in config:
        yield 'key {} is not in config. Keep your config clean'.format(key)
    elif not isinstance(config[key], basestring):
        yield 'You can only modify string values in your config. {} has type {}'.format(key, type(config[key]))
    else:
        config[key] = value
        save_config(config)
        yield 'set {} to {} in your config'.format(key, value)

