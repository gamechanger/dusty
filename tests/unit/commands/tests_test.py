from mock import patch, call

from ...testcases import DustyTestCase
from dusty.commands import tests

@patch('dusty.commands.tests.get_docker_client')
@patch('dusty.commands.tests.get_expanded_libs_specs')
@patch('dusty.commands.tests.ensure_image_exists')
@patch('dusty.commands.tests.sync_repos_by_app_name')
@patch('dusty.commands.tests.sync_repos_by_lib_name')
class TestTestsCommands(DustyTestCase):
    def setUp(self):
        super(TestTestsCommands, self).setUp()
        self.specs = {'apps': {
                        'app-a':{},
                        'app-b':{}},
                      'libs': {
                        'lib-a':{},
                        'lib-b':{}}}

    def test_test_app_or_lib_lib_not_found(self, fake_repos_by_lib, fake_repos_by_app, fake_ensure_iamge, fake_expanded_libs, fake_get_docker_client):
        with self.assertRaises(RuntimeError):
            tests.test_app_or_lib('lib-c')

    def test_test_app_or_lib_app_not_found(self, fake_repos_by_lib, fake_repos_by_app, fake_ensure_iamge, fake_expanded_libs, fake_get_docker_client):
        with self.assertRaises(RuntimeError):
            tests.test_app_or_lib('app-c')

