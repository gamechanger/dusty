from unittest import TestCase

from . import (get_all_test_cases, resources_for_test_case,
               nginx_config_for_test_case, docker_compose_yaml_for_test_case)

class TestCompilerTestCases(TestCase):
    def test_compiler_test_cases(test_case):
        for test_case in get_all_test_cases():
            pass
