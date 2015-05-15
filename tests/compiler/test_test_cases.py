from functools import wraps
from unittest import TestCase

from nose.tools import nottest

from . import (get_all_test_cases, resources_for_test_case, specs_for_test_case,
               assembled_for_test_case, nginx_config_for_test_case, docker_compose_yaml_for_test_case)
from dusty.compiler import spec_assembler

@nottest
def all_test_cases(test_func):
    @wraps(test_func)
    def inner(cls):
        for test_case in get_all_test_cases():
            case_specs = specs_for_test_case(test_case)
            assembled_specs = assembled_for_test_case(test_case)
            print "Running test case: {}".format(test_case)
            test_func(cls, test_case, case_specs, assembled_specs)
            print "Test case {} completed".format(test_case)
    return inner

class TestCompilerTestCases(TestCase):
    def test_compiler_test_cases(test_case):
        for test_case in get_all_test_cases():
            pass

class TestSpecAssemblerTestCases(TestCase):
    @all_test_cases
    def test_retrieves_downstream_apps(self, test_case, case_specs, assembled_specs):
        downstream_apps = spec_assembler._get_active_apps(case_specs)
        assembled_apps = set(assembled_specs['apps'].keys())
        self.assertEqual(downstream_apps, assembled_apps)

    @all_test_cases
    def test_expands_libs_in_apps(self, test_case, case_specs, assembled_specs):
        spec_assembler._expand_libs_in_apps(case_specs)
        for app_name, app in case_specs['apps'].iteritems():
            self.assertEqual(set(app.get('depends', {}).get('libs', [])), set(assembled_specs['apps'][app_name].get('depends', {}).get('libs', [])))

    @all_test_cases
    def test_assembles_specs(self, test_case, case_specs, assembled_specs):
        activated_bundles = assembled_specs['bundles'].keys()
        spec_assembler._get_expanded_active_specs(activated_bundles, case_specs)
        self.assertEqual(case_specs, assembled_specs)
