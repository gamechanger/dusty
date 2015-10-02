from mock import patch, call, Mock

from ...testcases import DustyTestCase
from ..utils import get_app_dusty_schema, get_lib_dusty_schema
from dusty.commands import test
from dusty.schemas.base_schema_class import DustySpecs
from dusty.source import Repo

@patch('dusty.commands.test.initialize_docker_vm')
@patch('dusty.commands.test.get_docker_client')
@patch('dusty.commands.test.get_expanded_libs_specs')
@patch('dusty.commands.test.ensure_current_image')
@patch('dusty.systems.nfs.update_nfs_with_repos')
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

    def test_run_one_suite_lib_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(KeyError):
            test.run_one_suite('lib-c', '', [])

    def test_run_one_suite_app_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(KeyError):
            test.run_one_suite('app-c', '', [])

    def test_run_all_suites_lib_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(KeyError):
            test.run_all_suites('lib-c')

    def test_run_all_suites_app_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(KeyError):
            test.run_all_suites('app-c')

    def test_run_one_suite_suite_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image, fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            test.run_one_suite('app-a', 'nosetests', [])

    @patch('dusty.commands.test._run_tests_with_image')
    @patch('dusty.command_file._write_commands_to_file')
    @patch('dusty.commands.test.sys.exit')
    def test_run_one_suite_lib_found(self, fake_exit, fake_write_commands, fake_run_tests, fake_lib_get_volumes,
                                            fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                            fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'
        fake_run_tests.return_value = 0

        test.run_one_suite('lib-a', 'nose', [])

        fake_update_nfs.assert_has_calls([])
        fake_ensure_current_image.assert_has_calls([call('lib-a', False)])
        fake_exit.assert_has_calls([call(0)])

    @patch('dusty.commands.test._run_tests_with_image')
    @patch('dusty.command_file._write_commands_to_file')
    @patch('dusty.commands.test.sys.exit')
    def test_run_one_suite_app_found(self, fake_exit, fake_write_commands, fake_run_tests, fake_lib_get_volumes,
                                            fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                            fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'
        fake_run_tests.return_value = 1

        test.run_one_suite('app-a','nose', [], force_recreate=True)

        fake_ensure_current_image.assert_has_calls([call('app-a', True)])
        fake_exit.assert_has_calls([call(1)])

    @patch('dusty.commands.test._run_tests_with_image')
    @patch('dusty.commands.test.sys.exit')
    def test_run_all_suites_lib_found(self, fake_exit, fake_run_tests, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_run_tests.side_effect = [0, 1]

        test.run_all_suites('multi-suite-lib', force_recreate=True)

        fake_run_tests.assert_has_calls([call('multi-suite-lib', 'nose1', None),
                                       call('multi-suite-lib', 'nose2', None)])
        fake_exit.assert_has_calls([call(1)])


    @patch('dusty.commands.test._run_tests_with_image')
    @patch('dusty.commands.test.sys.exit')
    def test_run_all_suites_app_found(self, fake_exit, fake_run_tests, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        fake_run_tests.return_value = 0

        test.run_all_suites('app-a')

        fake_run_tests.assert_has_calls([call('app-a', 'nose', None)])
        fake_exit.assert_has_calls([call(0)])

    def test_construct_test_command_invalid_name_app(self,fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            test._construct_test_command('app-a', 'run_tests', [])

    def test_construct_test_command_invalid_name_lib(self, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            test._construct_test_command('lib-a', 'run_tests', [])

    def test_construct_test_command_app_no_arguments(self, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        return_command = test._construct_test_command('app-a', 'nose', [])
        self.assertEquals('sh /command_files/dusty_command_file_app-a_test_nose.sh', return_command.strip())

    def test_construct_test_command_app_arguments(self, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        return_command = test._construct_test_command('app-a', 'nose', ['1', '2', '3'])
        self.assertEquals('sh /command_files/dusty_command_file_app-a_test_nose.sh 1 2 3', return_command.strip())

    def test_construct_test_command_lib_no_arguments(self, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        return_command = test._construct_test_command('lib-a', 'nose', [])
        self.assertEquals('sh /command_files/dusty_command_file_lib-a_test_nose.sh', return_command.strip())

    def test_construct_test_command_lib_arguments(self, fake_lib_get_volumes,
                                                 fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                                 fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_expanded_libs.return_value = self.specs
        return_command = test._construct_test_command('lib-a', 'nose', ['1', '2', '3'])
        self.assertEquals('sh /command_files/dusty_command_file_lib-a_test_nose.sh 1 2 3', return_command.strip())

    @patch('dusty.commands.test._update_test_repos')
    @patch('dusty.commands.test.make_test_command_files')
    @patch('dusty.commands.test.get_same_container_repos_from_spec')
    def test_pull_repos_and_sync_1(self, fake_same_container_repos, fake_make, fake_update_test, fake_lib_get_volumes,
                                    fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                    fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_app_spec = Mock()
        fake_specs = Mock()
        fake_repo_spec = Mock()
        fake_specs.get_app_or_lib.return_value = fake_app_spec
        fake_expanded_libs.return_value = fake_specs
        fake_same_container_repos.return_value = [fake_repo_spec]
        test.setup_for_test('app1', pull_repos=True)

        fake_update_test.assert_has_calls([call('app1')])
        fake_make.assert_has_calls([call('app1', fake_specs)])
        fake_update_nfs.assert_has_calls([call([fake_repo_spec])])

    @patch('dusty.commands.test._update_test_repos')
    @patch('dusty.commands.test.make_test_command_files')
    @patch('dusty.commands.test.get_same_container_repos_from_spec')
    def test_pull_repos_and_sync_2(self, fake_same_container_repos, fake_make, fake_update_test, fake_lib_get_volumes,
                                    fake_app_get_volumes, fake_update_nfs, fake_ensure_current_image,
                                    fake_expanded_libs, fake_get_docker_client, fake_initialize_vm):
        fake_app_spec = Mock()
        fake_specs = Mock()
        fake_repo_spec = Mock()
        fake_specs.get_app_or_lib.return_value = fake_app_spec
        fake_expanded_libs.return_value = fake_specs
        fake_same_container_repos.return_value = [fake_repo_spec]
        test.setup_for_test('app1')

        fake_update_test.assert_has_calls([])
        fake_make.assert_has_calls([call('app1', fake_specs)])
        fake_update_nfs.assert_has_calls([call([fake_repo_spec])])
