from mock import patch, call, Mock

from ...testcases import DustyTestCase
from ..utils import get_app_dusty_schema, get_lib_dusty_schema
from dusty.commands import test
from dusty.schemas.base_schema_class import DustySpecs
from dusty.source import Repo

@patch('dusty.commands.test.initialize_docker_vm')
@patch('dusty.commands.test.get_docker_client')
@patch('dusty.commands.test.get_expanded_libs_specs')
@patch('dusty.commands.test.ensure_test_image')
@patch('dusty.commands.test.sync_repos_by_specs')
@patch('dusty.compiler.compose.get_app_volume_mounts')
@patch('dusty.compiler.compose.get_lib_volume_mounts')
class TestTestsCommands(DustyTestCase):
    def setUp(self):
        super(TestTestsCommands, self).setUp()
        self.specs = self.make_test_specs({'apps': {
                        'app-a': get_app_dusty_schema({'test': {'suites': [{'name': 'nose', 'command': ['nosetests app-a']}]},
                                                       'mount': '/app-a'},
                                                      name='app-a')},
                      'libs': {
                        'lib-a': get_lib_dusty_schema({'test': {'suites': [{'name': 'nose', 'command': ['nosetests lib-a']}]},
                                                       'mount': '/lib-a'},
                                                      name='lib-a'),
                        'multi-suite-lib': get_lib_dusty_schema({'test': {'suites': [{'name': 'nose1', 'command': ['nosetests lib-a']},
                                                                                     {'name': 'nose2', 'command': ['nosetests lib-a']}]},
                                                       'mount': '/lib-a'},
                                                      name='lib-a')}})

    def test_run_app_or_lib_tests_lib_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(KeyError):
            test.run_app_or_lib_tests('lib-c', '', [])

    def test_run_app_or_lib_tests_app_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(KeyError):
            test.run_app_or_lib_tests('app-c', '', [])

    def test_run_all_app_or_lib_suites_lib_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(KeyError):
            test.run_all_app_or_lib_suites('lib-c')

    def test_run_all_app_or_lib_suites_app_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(KeyError):
            test.run_all_app_or_lib_suites('app-c')

    def test_run_app_or_lib_tests_suite_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            test.run_app_or_lib_tests('app-a', 'nosetests', [])

    @patch('dusty.commands.test._run_tests_with_image')
    @patch('dusty.command_file._write_commands_to_file')
    def test_run_app_or_lib_tests_lib_found(self, fake_write_commands, fake_run_tests, fake_lib_get_volumes,
                                            fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image,
                                            fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'

        test.run_app_or_lib_tests('lib-a', 'nose', [])

        fake_repos_by_specs.assert_has_calls([])
        fake_ensure_image.assert_has_calls([call('docker-client',
                                                 'lib-a',
                                                 self.specs,
                                                 force_recreate=False)])

    @patch('dusty.commands.test._run_tests_with_image')
    @patch('dusty.command_file._write_commands_to_file')
    def test_run_app_or_lib_tests_app_found(self, fake_write_commands, fake_run_tests, fake_lib_get_volumes,
                                            fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image,
                                            fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'

        test.run_app_or_lib_tests('app-a','nose', [], force_recreate=True)

        fake_ensure_image.assert_has_calls([call('docker-client',
                                                 'app-a',
                                                 self.specs,
                                                 force_recreate=True)])

    @patch('dusty.commands.test.run_app_or_lib_tests')
    @patch('dusty.commands.test.sys.exit')
    def test_run_all_app_or_lib_suites_lib_found(self, fake_exit, fake_run_app, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_run_app.side_effect = [0, 1]

        test.run_all_app_or_lib_suites('multi-suite-lib', force_recreate=True)

        fake_run_app.assert_has_calls([call('multi-suite-lib', 'nose1', [], False, True),
                                       call('multi-suite-lib', 'nose2', [], False)])
        fake_exit.assert_has_calls([call(1)])


    @patch('dusty.commands.test.run_app_or_lib_tests')
    @patch('dusty.commands.test.sys.exit')
    def test_run_all_app_or_lib_suites_app_found(self, fake_exit, fake_run_app, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_run_app.return_value = 0

        test.run_all_app_or_lib_suites('app-a')

        fake_run_app.assert_has_calls([call('app-a', 'nose', [], False)])
        fake_exit.assert_has_calls([call(0)])

    def test_construct_test_command_invalid_name_app(self, *args):
        with self.assertRaises(RuntimeError):
            test._construct_test_command(self.specs['apps']['app-a'], 'run_tests', [])

    def test_construct_test_command_invalid_name_lib(self, *args):
        with self.assertRaises(RuntimeError):
            test._construct_test_command(self.specs['libs']['lib-a'], 'run_tests', [])

    def test_construct_test_command_app_no_arguments(self, *args):
        return_command = test._construct_test_command(self.specs['apps']['app-a'], 'nose', [])
        self.assertEquals('sh /command_files/dusty_command_file_app-a_test_nose.sh', return_command.strip())

    def test_construct_test_command_app_arguments(self, *args):
        return_command = test._construct_test_command(self.specs['apps']['app-a'], 'nose', ['1', '2', '3'])
        self.assertEquals('sh /command_files/dusty_command_file_app-a_test_nose.sh 1 2 3', return_command.strip())

    def test_construct_test_command_lib_no_arguments(self, *args):
        return_command = test._construct_test_command(self.specs['libs']['lib-a'], 'nose', [])
        self.assertEquals('sh /command_files/dusty_command_file_lib-a_test_nose.sh', return_command.strip())

    def test_construct_test_command_lib_arguments(self, *args):
        return_command = test._construct_test_command(self.specs['libs']['lib-a'], 'nose', ['1', '2', '3'])
        self.assertEquals('sh /command_files/dusty_command_file_lib-a_test_nose.sh 1 2 3', return_command.strip())

    @patch('dusty.commands.test._update_test_repos')
    @patch('dusty.commands.test.make_test_command_files')
    def test_pull_repos_and_sync_1(self, fake_make, fake_update_test, fake_lib_get_volumes,
                                    fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image,
                                    fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_app_spec = Mock()
        fake_specs = Mock()
        fake_specs.get_app_or_lib.return_value = fake_app_spec
        fake_expanded_libs.return_value = fake_specs
        test.pull_repos_and_sync('app1', pull_repos=True)

        fake_update_test.assert_has_calls([call('app1')])
        fake_make.assert_has_calls([call('app1', fake_specs)])
        fake_repos_by_specs.assert_has_calls([call([fake_app_spec])])

    @patch('dusty.commands.test._update_test_repos')
    @patch('dusty.commands.test.make_test_command_files')
    def test_pull_repos_and_sync_2(self, fake_make, fake_update_test, fake_lib_get_volumes,
                                    fake_app_get_volumes, fake_repos_by_specs, fake_ensure_image,
                                    fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_app_spec = Mock()
        fake_specs = Mock()
        fake_specs.get_app_or_lib.return_value = fake_app_spec
        fake_expanded_libs.return_value = fake_specs
        test.pull_repos_and_sync('app1')

        fake_update_test.assert_has_calls([])
        fake_make.assert_has_calls([call('app1', fake_specs)])
        fake_repos_by_specs.assert_has_calls([call([fake_app_spec])])
