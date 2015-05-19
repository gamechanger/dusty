from ..config import get_config, save_config

def list_config():
     yield str(get_config())

def set_value(key, value):
    config = get_config()
    config[key] = value
    save_config(config)
    yield 'set {} to {} in your config'.format(key, value)

