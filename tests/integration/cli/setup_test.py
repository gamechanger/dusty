from mock import patch

from ...testcases import DustyIntegrationTestCase

from dusty import constants
from dusty.config import save_config_value

class TestSetupCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestSetupCLI, self).setUp()
        save_config_value(constants.CONFIG_SETUP_KEY, False)
        save_config_value(constants.CONFIG_SPECS_REPO_KEY, '')
        save_config_value(constants.CONFIG_MAC_USERNAME_KEY, 'nobody')

    @patch('dusty.commands.setup._get_recommended_vm_size')
    @patch('dusty.commands.setup._get_raw_input')
    def test_setup_defaults(self, fake_raw_input, fake_vm_size):
        fake_vm_size.return_value = 2048
        fake_raw_input.side_effect = ['y', '', 'y']
        self.run_command('setup --no-update')
        self.assertConfigValue(constants.CONFIG_MAC_USERNAME_KEY, self.current_user)
        self.assertConfigValue(constants.CONFIG_SPECS_REPO_KEY, 'github.com/gamechanger/dusty-example-specs')
        self.assertConfigValue(constants.CONFIG_VM_MEM_SIZE, 2048)

    @patch('dusty.commands.setup._get_raw_input')
    def test_setup_override_user(self, fake_raw_input):
        fake_raw_input.side_effect = ['n', self.current_user, '', 'y']
        self.run_command('setup --no-update')
        self.assertConfigValue(constants.CONFIG_MAC_USERNAME_KEY, self.current_user)

    @patch('dusty.commands.setup._get_raw_input')
    def test_setup_override_specs(self, fake_raw_input):
        fake_raw_input.side_effect = ['y', 'github.com/gamechanger/dusty-specs', 'y']
        self.run_command('setup --no-update')
        self.assertConfigValue(constants.CONFIG_SPECS_REPO_KEY, 'github.com/gamechanger/dusty-specs')

    @patch('dusty.commands.setup._get_raw_input')
    def test_setup_override_memory(self, fake_raw_input):
        fake_raw_input.side_effect = ['y', '', 'n', '1024']
        self.run_command('setup --no-update')
        self.assertConfigValue(constants.CONFIG_VM_MEM_SIZE, 1024)

    def test_setup_flags(self):
        self.run_command('setup --no-update --mac_username={} --default_specs_repo=github.com/gamechanger/dusty-specs --boot2docker_vm_memory=1024'.format(self.current_user))
        self.assertConfigValue(constants.CONFIG_MAC_USERNAME_KEY, self.current_user)
        self.assertConfigValue(constants.CONFIG_SPECS_REPO_KEY, 'github.com/gamechanger/dusty-specs')
        self.assertConfigValue(constants.CONFIG_VM_MEM_SIZE, 1024)
