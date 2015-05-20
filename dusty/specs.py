import os
import glob
import yaml

from .config import get_config_value, assert_config_key
from .source import repo_path

def get_specs_repo():
    return get_config_value('specs_repo')

def get_specs_path():
    return repo_path(get_specs_repo())

def get_specs():
    specs_path = get_specs_path()
    return get_specs_from_path(specs_path)

def get_specs_from_path(specs_path):
    specs = {}
    for key in ['bundles', 'apps', 'libs', 'services']:
        specs[key] = {}
        key_path = os.path.join(specs_path, key)
        for spec_path in glob.glob('{}/*.yml'.format(key_path)):
            spec_name = os.path.splitext(os.path.split(spec_path)[-1])[0]
            with open(spec_path, 'r') as f:
                specs[key][spec_name] = yaml.load(f.read())
    return specs

