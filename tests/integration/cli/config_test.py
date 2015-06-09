import yaml
import docopt

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture
from dusty.config import get_config

class TestConfigCLI(DustyIntegrationTestCase):
    def test_config_list_returns(self):
        result = self.run_command('config list')
        self.assertInSameLine(result, 'Key', 'Description', 'Value')
        self.assertInSameLine(result, 'bundles', '[]')
        self.assertInSameLine(result, 'mac_username', self.current_user)
        self.assertInSameLine(result, 'setup_has_run', 'True')

    def test_config_listvalues_returns(self):
        result = yaml.load(self.run_command('config listvalues'))
        self.assertItemsEqual(result, get_config())

    def test_config_set_fails_with_no_args(self):
        with self.assertRaises(docopt.DocoptExit):
            self.run_command('config set')

    def test_config_set_fails_on_nonexistent_key(self):
        with self.assertRaises(self.CommandError):
            self.run_command('config set bacon-level extreme')

    def test_config_set_works_with_valid_input(self):
        self.run_command('config set nginx_includes_dir /var/nginx')
        result = yaml.load(self.run_command('config listvalues'))
        self.assertEqual(result['nginx_includes_dir'], '/var/nginx')
