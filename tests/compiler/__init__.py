import os
from pkg_resources import resource_isdir, resource_listdir, resource_string
import yaml

from nose.tools import nottest

from dusty.specs import get_specs_from_path

@nottest
def get_all_test_configs():
    return resource_listdir(__name__, 'test_configs')

@nottest
def resources_for_test_config(test_config):
    resources = {}
    for key in ['bundles', 'apps', 'libs', 'services']:
        key_path = 'test_configs/{}/{}'.format(test_config, key)
        if resource_isdir(__name__, key_path):
            resources[key] = {resource_name: resource_string(__name__, '{}/{}'.format(key_path, resource_name))
                              for resource_name in resource_listdir(__name__, key_path)}
    return resources

@nottest
def specs_for_test_config(test_config):
    case_path = '{}/test_configs/{}/'.format(__path__[0], test_config)
    return get_specs_from_path(case_path)

@nottest
def assembled_specs_for_test_config(test_config):
    assembled_file = "{}/test_configs/{}/assembled_spec.yml".format(__path__[0], test_config)
    with open(assembled_file, 'r') as f:
        return yaml.load(f.read())

@nottest
def nginx_config_for_test_config(test_config):
    return resource_string(__name__, 'test_configs/{}/nginx.conf'.format(test_config))

@nottest
def docker_compose_yaml_for_test_config(test_config):
    return resource_string(__name__, 'test_configs/{}/docker-compose.yml'.format(test_config))
