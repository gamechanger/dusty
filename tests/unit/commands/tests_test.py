from mock import patch, call

from ...testcases import DustyTestCase
from dusty.commands import tests

@patch('dusty.commands.tests.get_docker_client')
@patch('dusty.commands.tests.get_expanded_libs_specs')
@patch('dusty.commands.tests.ensure_image_exists')
@patch('dusty.commands.tests.sync_repos_by_app_name')
@patch('dusty.commands.tests.sync_repos_by_lib_name')
@patch('dusty.commands.tests.get_app_volume_mounts')
@patch('dusty.commands.tests.get_lib_volume_mounts')
class TestTestsCommands(DustyTestCase):
    def setUp(self):
        super(TestTestsCommands, self).setUp()
        self.specs = {'apps': {
                        'app-a': {'test': 'fake_app_a'},
                        'app-b': {'test': 'fake_app_b'}},
                      'libs': {
                        'lib-a': {'test': 'fake_lib_a'},
                        'lib-b': {'test': 'fake_lib_b'}}}

    def test_test_app_or_lib_lib_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_iamge, fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            tests.test_app_or_lib('lib-c')

    def test_test_app_or_lib_app_not_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_iamge, fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.return_value = self.specs
        with self.assertRaises(RuntimeError):
            tests.test_app_or_lib('app-c')

    def test_test_app_or_lib_lib_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_iamge, fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'

        tests.test_app_or_lib('lib-a')

        fake_repos_by_lib.assert_has_calls([call(self.specs, ['lib-a'])])
        fake_repos_by_app.assert_has_calls([])
        fake_ensure_iamge.assert_has_calls([call('docker-client',
                                                 'fake_lib_a',
                                                 'lib-a_dusty_testing/image',
                                                 volumes=['/host/route:/container/route'],
                                                 force_recreate=False)])

    def test_test_app_or_lib_app_found(self, fake_lib_get_volumes, fake_app_get_volumes, fake_repos_by_lib, fake_repos_by_app, fake_ensure_iamge, fake_expanded_libs, fake_get_docker_client):
        fake_expanded_libs.return_value = self.specs
        fake_lib_get_volumes.return_value = ['/host/route:/container/route']
        fake_app_get_volumes.return_value = []
        fake_get_docker_client.return_value = 'docker-client'

        tests.test_app_or_lib('app-a', force_recreate=True)

        fake_repos_by_lib.assert_has_calls([])
        fake_repos_by_app.assert_has_calls([call(self.specs, ['app-a'])])
        fake_ensure_iamge.assert_has_calls([call('docker-client',
                                                 'fake_app_a',
                                                 'app-a_dusty_testing/image',
                                                 volumes=[],
                                                 force_recreate=True)])
