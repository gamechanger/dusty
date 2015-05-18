import os
from pkg_resources import resource_isdir, resource_listdir, resource_string
import yaml

from nose.tools import nottest

from dusty.specs import get_specs_from_path

@nottest
def get_all_test_cases():
    return resource_listdir(__name__, 'test_cases')

@nottest
def resources_for_test_case(test_case):
    resources = {}
    for key in ['bundles', 'apps', 'libs', 'services']:
        key_path = 'test_cases/{}/{}'.format(test_case, key)
        if resource_isdir(__name__, key_path):
            resources[key] = {resource_name: resource_string(__name__, '{}/{}'.format(key_path, resource_name))
                              for resource_name in resource_listdir(__name__, key_path)}
    return resources

@nottest
def specs_for_test_case(test_case):
    case_path = '{}/test_cases/{}/'.format(__path__[0], test_case)
    return get_specs_from_path(case_path)

@nottest
def assembled_for_test_case(test_case):
    assembled_file = "{}/test_cases/{}/assembled_spec.yml".format(__path__[0], test_case)
    with open(assembled_file, 'r') as f:
        return yaml.load(f.read())

@nottest
def nginx_config_for_test_case(test_case):
    return resource_string(__name__, 'test_cases/{}/nginx.conf'.format(test_case))

@nottest
def docker_compose_yaml_for_test_case(test_case):
    return resource_string(__name__, 'test_cases/{}/docker-compose.yml'.format(test_case))
