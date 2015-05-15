import os
import glob
import yaml

from .config import get_config_value

def get_specs(override_specs_path=None):
    if override_specs_path is None:
        specs_path = get_config_value('specs_path')
    else:
        specs_path = override_specs_path
    specs = {}
    for key in ['bundles', 'apps', 'libs', 'services']:
        specs[key] = {}
        key_path = os.path.join(specs_path, key)
        for spec_path in glob.glob('{}/*.yml'.format(key_path)):
            spec_name = os.path.splitext(os.path.split(spec_path)[-1])[0]
            with open(spec_path, 'r') as f:
                specs[key][spec_name] = yaml.load(f.read())
    return specs
