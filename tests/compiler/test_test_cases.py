from unittest import TestCase

from . import (get_all_test_cases, resources_for_test_case,
               nginx_config_for_test_case, docker_compose_yaml_for_test_case)

class TestCompilerTestCases(TestCase):
    def test_compiler_test_cases(test_case):
        for test_case in get_all_test_cases():
            pass


class TestSpecAssemblerTestCases(TestCase):
    def runTests(self):
        for test_case in get_all_test_cases():
            self.test_case = test_case
            self.test_case_specs = resources_for_test_case(test_case)
            super(TestSpecAssemblerTestCases, self).runTests()

    def test_retrieves_downstream_apps(self):
        print "test_case: {}".format(self.test_case)
        pass

    def test_expands_libs_in_apps(self):
        print "test_case: {}".format(self.test_case)
        pass

    def test_filters_bundles(self):
        print "test_case: {}".format(self.test_case)
        pass

    def test_filters_apps(self):
        print "test_case: {}".format(self.test_case)
        pass

    def test_filters_libs(self):
        print "test_case: {}".format(self.test_case)
        pass

    def test_filters_services(self):
        print "test_case: {}".format(self.test_case)
        raise

    def test_assembles_specs(self):
        print "test_case: {}".format(self.test_case)
        pass
