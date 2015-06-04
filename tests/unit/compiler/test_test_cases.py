from functools import wraps
from mock import patch

from nose.tools import nottest

from . import (get_all_test_configs, resources_for_test_config, specs_for_test_config,
               assembled_specs_for_test_config, nginx_config_for_test_config, docker_compose_yaml_for_test_config)
from dusty.compiler import spec_assembler
from ...testcases import DustyTestCase
from dusty import constants

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

class TestCompilerTestCases(DustyTestCase):
    def test_compiler_test_configs(test_config):
        for test_config in get_all_test_configs():
            pass

class TestSpecAssemblerTestCases(DustyTestCase):
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
    def test_assembles_specs(self, test_config, case_specs, assembled_specs, *args):
        self.maxDiff = None
        bundles = case_specs[constants.CONFIG_BUNDLES_KEY].keys()
        @patch('dusty.compiler.spec_assembler._get_active_bundles', return_value=bundles)
        def run_patched_assembler(case_specs, *args):
            spec_assembler._get_expanded_active_specs(case_specs)
        run_patched_assembler(case_specs)
        self.assertEqual(case_specs, assembled_specs)

    def test_get_dependent_traverses_tree(self):
        specs = {
            'apps': {
                'app1': {
                    'depends': {'apps': ['app2']}
                },
                'app2': {
                    'depends': {'apps': ['app3']}
                },
                'app3': {
                    'depends': {'apps': ['app4', 'app5']}
                },
                'app4': {
                    'depends': {'apps': ['app5']}
                },
                'app5': {},
                'app6': {}
            }
        }
        self.assertEqual(set(['app2', 'app3', 'app4', 'app5']),
            spec_assembler._get_dependent('apps', 'app1', specs, 'apps'))

    def test_get_dependent_root_type(self):
        specs = {
            'apps': {
                'app1': {
                    'depends': {
                        'apps': ['app2'],
                        'libs': ['lib1']
                    }
                },
                'app2': {}
            },
            'libs': {
                'lib1':{
                    'depends': {'libs': ['lib2']}
                },
                'lib2':{},
                'lib3': {}
            }
        }
        self.assertEqual(set(['lib1', 'lib2']),
            spec_assembler._get_dependent('libs', 'app1', specs, 'apps'))

class TestExpectedRunningContainers(DustyTestCase):
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_get_expected_number_of_running_containers_1(self, fake_get_assembled_specs):
        specs = {'apps': {
                    'app1': {},
                    'app2': {}},
                 'libs': {
                    'lib1': {},
                    'lib2': {}
                 },
                 'services': {
                    'sev1': {},
                    'sev2': {}
                 },
                 constants.CONFIG_BUNDLES_KEY: {
                    'bun1': {},
                    'bun2': {}
                 }}
        fake_get_assembled_specs.return_value = specs
        self.assertEqual(spec_assembler.get_expected_number_of_running_containers(), 4)


    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_get_expected_number_of_running_containers_2(self, fake_get_assembled_specs):
        specs = {'apps': {
                    'app1': {}},
                 'libs': {
                    'lib1': {},
                    'lib2': {}
                 },
                 'services': {
                    'sev1': {},
                    'sev2': {},
                    'sev3': {}
                 },
                 constants.CONFIG_BUNDLES_KEY: {
                    'bun1': {},
                    'bun2': {},
                    'bun1': {},
                    'bun2': {}
                 }}
        fake_get_assembled_specs.return_value = specs
        self.assertEqual(spec_assembler.get_expected_number_of_running_containers(), 4)

class TestSpecAssemblerGetRepoTestCases(DustyTestCase):
    def test_get_repo_of_app_or_service_app(self):
        self.assertEqual(spec_assembler.get_repo_of_app_or_library('app-a'), 'github.com/app/a')

    def test_get_repo_of_app_or_service_lib(self):
        self.assertEqual(spec_assembler.get_repo_of_app_or_library('lib-a'), 'github.com/lib/a')

    def test_get_repo_of_app_or_service_neither(self):
        with self.assertRaises(KeyError):
            spec_assembler.get_repo_of_app_or_library('lib-b')
