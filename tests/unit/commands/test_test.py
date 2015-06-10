from mock import patch, call

from ...testcases import DustyTestCase
from ..utils import get_app_dusty_schema, get_lib_dusty_schema
from dusty.commands import test


@patch('dusty.commands.test.get_docker_client')
@patch('dusty.commands.test.get_expanded_libs_specs')
@patch('dusty.commands.test.ensure_image_exists')
@patch('dusty.commands.test.sync_repos_by_app_name')
@patch('dusty.commands.test.sync_repos_by_lib_name')
@patch('dusty.commands.test.get_app_volume_mounts')
@patch('dusty.commands.test.get_lib_volume_mounts')
class TestTestsCommands(DustyTestCase):
    def setUp(self):
        super(TestTestsCommands, self).setUp()
        self.specs = {'apps': {
                        'app-a': get_app_dusty_schema({'test': {'suites': [{'name': 'nose', 'command': 'nosetests app-a'}]}}),
                        'app-b': get_app_dusty_schema({'test': {'fake_app_b': True}})},
                      'libs': {
                        'lib-a': get_lib_dusty_schema({'test': {'suites': [{'name': 'nose', 'command': 'nosetests lib-a'}]}}),
                        'lib-b': get_lib_dusty_schema({'test': {'fake_app_b': True}})}}

    def test_run_app_or_lib_tests_lib_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_image, fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            test.run_app_or_lib_tests('lib-c', '', [])

    def test_run_app_or_lib_tests_app_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_image, fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.reurn_value = self.specs
        with self.assertRaises(RuntimeError):
            test.run_app_or_lib_tests('app-c', '', [])

    def test_run_app_or_lib_tests_suite_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_image, fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.reurn_value = self.specs
        with self.assertRaises(RuntimeError):
            test.run_app_or_lib_tests('app-a', 'nosetests', [])

    @patch('dusty.commands.test._run_tests_with_image')
    def test_run_app_or_lib_tests_lib_found(self, fake_run_tests, fake_lib_get_volumes, fake_app_get_volumes,
                                            fake_repos_by_lib, fake_repos_by_app, fake_ensure_image,
                                            fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'

        test.run_app_or_lib_tests('lib-a', 'nose', [])

        fake_repos_by_lib.assert_has_calls([call(self.specs, ['lib-a'])])
        fake_repos_by_app.assert_has_calls([])
        fake_ensure_image.assert_has_calls([call('docker-client',
                                                 {'suites': [{'name': 'nose', 'command': 'nosetests lib-a'}]},
                                                 'lib-a_dusty_testing/image',
                                                 volumes=['/host/route:/container/route'],
                                                 force_recreate=False)])

    @patch('dusty.commands.test._run_tests_with_image')
    def test_run_app_or_lib_tests_app_found(self, fake_run_tests, fake_lib_get_volumes, fake_app_get_volumes,
                                            fake_repos_by_lib, fake_repos_by_app, fake_ensure_image,
                                            fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'

        test.run_app_or_lib_tests('app-a','nose', [], force_recreate=True)

        fake_repos_by_lib.assert_has_calls([])
        fake_repos_by_app.assert_has_calls([call(self.specs, ['app-a'])])
        fake_ensure_image.assert_has_calls([call('docker-client',
                                                 {'suites': [{'name': 'nose', 'command': 'nosetests app-a'}]},
                                                 'app-a_dusty_testing/image',
                                                 volumes=[],
                                                 force_recreate=True)])
