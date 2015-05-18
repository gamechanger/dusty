from functools import wraps
from unittest import TestCase

from nose.tools import nottest

from . import (get_all_test_configs, resources_for_test_config, specs_for_test_config,
               assembled_specs_for_test_config, nginx_config_for_test_config, docker_compose_yaml_for_test_config)
from dusty.compiler import spec_assembler

@nottest
def all_test_configs(test_func):
    @wraps(test_func)
    def inner(cls):
        for test_config in get_all_test_configs():
            case_specs = specs_for_test_config(test_config)
            assembled_specs = assembled_specs_for_test_config(test_config)
            print "Running test case: {}".format(test_config)
            test_func(cls, test_config, case_specs, assembled_specs)
            print "Test case {} completed".format(test_config)
    return inner

class TestCompilerTestCases(TestCase):
    def test_compiler_test_configs(test_config):
        for test_config in get_all_test_configs():
            pass

class TestSpecAssemblerTestCases(TestCase):
    @all_test_configs
    def test_retrieves_downstream_apps(self, test_config, case_specs, assembled_specs):
        downstream_apps = spec_assembler._get_referenced_apps(case_specs)
        assembled_apps = set(assembled_specs['apps'].keys())
        self.assertEqual(downstream_apps, assembled_apps)

    @all_test_configs
    def test_expands_libs_in_apps(self, test_config, case_specs, assembled_specs):
        spec_assembler._expand_libs_in_apps(case_specs)
        for app_name, app in case_specs['apps'].iteritems():
            self.assertEqual(set(app.get('depends', {}).get('libs', [])), set(assembled_specs['apps'][app_name].get('depends', {}).get('libs', [])))

    @all_test_configs
    def test_assembles_specs(self, test_config, case_specs, assembled_specs):
        self.maxDiff = None
        activated_bundles = assembled_specs['bundles'].keys()
        spec_assembler._get_expanded_active_specs(activated_bundles, case_specs)
        self.assertEqual(case_specs, assembled_specs)
