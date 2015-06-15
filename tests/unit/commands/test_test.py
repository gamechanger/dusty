from mock import patch, call

from ...testcases import DustyTestCase
from ..utils import get_app_dusty_schema, get_lib_dusty_schema
from dusty.commands import test

@patch('dusty.commands.test.initialize_docker_vm')
@patch('dusty.commands.test.get_docker_client')
@patch('dusty.commands.test.get_expanded_libs_specs')
@patch('dusty.commands.test.ensure_test_image')
@patch('dusty.commands.test.sync_repos_by_app_name')
@patch('dusty.commands.test.sync_repos_by_lib_name')
@patch('dusty.compiler.compose.get_app_volume_mounts')
@patch('dusty.compiler.compose.get_lib_volume_mounts')
class TestTestsCommands(DustyTestCase):
    def setUp(self):
        super(TestTestsCommands, self).setUp()
        self.specs = {'apps': {
                        'app-a': get_app_dusty_schema({'test': {'suites': [{'name': 'nose', 'command': 'nosetests app-a'}]}})},
                      'libs': {
                        'lib-a': get_lib_dusty_schema({'test': {'suites': [{'name': 'nose', 'command': 'nosetests lib-a'}]}})}}

    def test_run_app_or_lib_tests_lib_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            test.run_app_or_lib_tests('lib-c', '', [])

    def test_run_app_or_lib_tests_app_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            test.run_app_or_lib_tests('app-c', '', [])

    def test_run_app_or_lib_tests_suite_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            test.run_app_or_lib_tests('app-a', 'nosetests', [])

    @patch('dusty.commands.test._run_tests_with_image')
    def test_run_app_or_lib_tests_lib_found(self, fake_run_tests, fake_lib_get_volumes, fake_app_get_volumes,
                                            fake_repos_by_lib, fake_repos_by_app, fake_ensure_image,
                                            fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'

        test.run_app_or_lib_tests('lib-a', 'nose', [])

        fake_repos_by_lib.assert_has_calls([call(self.specs, ['lib-a'])])
        fake_repos_by_app.assert_has_calls([])
        fake_ensure_image.assert_has_calls([call('docker-client',
                                                 'lib-a',
                                                 self.specs,
                                                 force_recreate=False)])

    @patch('dusty.commands.test._run_tests_with_image')
    def test_run_app_or_lib_tests_app_found(self, fake_run_tests, fake_lib_get_volumes, fake_app_get_volumes,
                                            fake_repos_by_lib, fake_repos_by_app, fake_ensure_image,
                                            fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'

        test.run_app_or_lib_tests('app-a','nose', [], force_recreate=True)

        fake_repos_by_lib.assert_has_calls([])
        fake_repos_by_app.assert_has_calls([call(self.specs, ['app-a'])])
        fake_ensure_image.assert_has_calls([call('docker-client',
                                                 'app-a',
                                                 self.specs,
                                                 force_recreate=True)])

    def test_construct_test_command_invalid_name_app(self, *args):
        with self.assertRaises(RuntimeError):
            test._construct_test_command(self.specs['apps']['app-a'], 'run_tests', [])

    def test_construct_test_command_invalid_name_lib(self, *args):
        with self.assertRaises(RuntimeError):
            test._construct_test_command(self.specs['libs']['lib-a'], 'run_tests', [])

    def test_construct_test_command_app_no_arguments(self, *args):
        return_command = test._construct_test_command(self.specs['apps']['app-a'], 'nose', [])
        self.assertEquals('sh -c "nosetests app-a"', return_command.strip())

    def test_construct_test_command_app_arguments(self, *args):
        return_command = test._construct_test_command(self.specs['apps']['app-a'], 'nose', ['1', '2', '3'])
        self.assertEquals('sh -c "nosetests app-a 1 2 3"', return_command.strip())

    def test_construct_test_command_lib_no_arguments(self, *args):
        return_command = test._construct_test_command(self.specs['libs']['lib-a'], 'nose', [])
        self.assertEquals('sh -c "nosetests lib-a"', return_command.strip())

    def test_construct_test_command_lib_arguments(self, *args):
        return_command = test._construct_test_command(self.specs['libs']['lib-a'], 'nose', ['1', '2', '3'])
        self.assertEquals('sh -c "nosetests lib-a 1 2 3"', return_command.strip())
