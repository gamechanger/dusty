from functools import wraps
from unittest import TestCase

from nose.tools import nottest

from . import (get_all_test_cases, resources_for_test_case, specs_for_test_case,
               assembled_for_test_case, nginx_config_for_test_case, docker_compose_yaml_for_test_case)
from dusty.compiler import spec_assembler

class TestCompilerTestCases(TestCase):
    def test_compiler_test_cases(test_case):
        for test_case in get_all_test_cases():
            pass

@nottest
def all_test_cases(test_func):
    @wraps(test_func)
    def inner(cls):
        for test_case in get_all_test_cases():
            case_specs = specs_for_test_case(test_case)
            assembled_specs = assembled_for_test_case(test_case)
            print "test_case: {}".format(test_case)
            test_func(cls, test_case, case_specs, assembled_specs)
    return inner


class TestSpecAssemblerTestCases(TestCase):
    def setUp(self):
        self.test_cases = get_all_test_cases()
        self.test_case_specs = [resources_for_test_case(test_case) for test_case in self.test_cases]

    @all_test_cases
    def test_retrieves_downstream_apps(self, test_case, case_specs, assembled_specs):
        downstream_apps = spec_assembler._get_active_apps(case_specs)
        assembled_apps = set(assembled_specs['apps'].keys())
        self.assertEqual(downstream_apps, assembled_apps)

    @all_test_cases
    def test_expands_libs_in_apps(self, test_case, case_specs, assembled_specs):
        pass

    @all_test_cases
    def test_filters_bundles(self, test_case, case_specs, assembled_specs):
        pass

    @all_test_cases
    def test_filters_apps(self, test_case, case_specs, assembled_specs):
        pass

    @all_test_cases
    def test_filters_libs(self, test_case, case_specs, assembled_specs):
        pass

    @all_test_cases
    def test_filters_services(self, test_case, case_specs, assembled_specs):
        pass

    @all_test_cases
    def test_assembles_specs(self, test_case, case_specs, assembled_specs):
        pass
