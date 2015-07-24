from mock import patch, call, Mock

from ...testcases import DustyTestCase
from dusty.commands.setup import (_get_mac_username, setup_dusty_config, complete_setup,
                                  _get_boot2docker_vm_size)
from dusty.payload import Payload
from dusty import constants

class TestSetupCommands(DustyTestCase):
    @patch('dusty.commands.setup.subprocess.check_output')
    @patch('dusty.commands.setup._get_raw_input')
    def test_get_mac_username_no(self, fake_raw_input, fake_check_output):
        fake_raw_input.return_value = 'n'
        fake_check_output.return_value = 'user\n'
        result = _get_mac_username()
        self.assertEqual(result, 'n')

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup.subprocess.check_output')
    @patch('dusty.commands.setup._get_raw_input')
    def test_get_mac_username_yes(self, fake_raw_input, fake_check_output, fake_pwnam):
        fake_raw_input.return_value = 'y'
        fake_check_output.return_value = 'user\n'
        result = _get_mac_username()
        self.assertEqual(result, 'user')

    def factory_file_side_effect(self, file_compare_name):
        def is_file_side_effect(file_name):
            if file_name == file_compare_name:
                return True
            return False
        return is_file_side_effect

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    @patch('dusty.commands.setup._get_boot2docker_vm_size')
    def test_setup_dusty_config(self, fake_get_vm_size, fake_get_mac, fake_get_default_specs, fake_pwnam):
        fake_get_mac.return_value = 'user'
        fake_get_default_specs.return_value = 'github.com/gamechanger/dusty'
        fake_get_vm_size.return_value = 6
        expected_dict_argument = {constants.CONFIG_MAC_USERNAME_KEY: 'user',
                                  constants.CONFIG_SPECS_REPO_KEY: 'github.com/gamechanger/dusty',
                                  constants.CONFIG_VM_MEM_SIZE: 6}
        return_payload = setup_dusty_config()
        self.assertEqual(return_payload.fn, complete_setup)
        self.assertEqual(return_payload.args[0], expected_dict_argument)

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    @patch('dusty.commands.setup._get_boot2docker_vm_size')
    def test_setup_dusty_config_pass_arguments_1(self, fake_get_vm_size, fake_get_mac, fake_get_default_specs, fake_pwnam):
        setup_dusty_config(mac_username='1',
                           specs_repo='2')
        fake_get_vm_size.assert_has_calls([call()])
        fake_get_mac.assert_has_calls([])
        fake_get_default_specs.assert_has_calls([])

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    @patch('dusty.commands.setup._get_boot2docker_vm_size')
    def test_setup_dusty_config_pass_arguments_2(self, fake_get_vm_size, fake_get_mac, fake_get_default_specs, fake_pwnam):
        setup_dusty_config(mac_username='1')
        fake_get_vm_size.assert_has_calls([call()])
        fake_get_mac.assert_has_calls([])
        fake_get_default_specs.assert_has_calls([call()])

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    @patch('dusty.commands.setup._get_boot2docker_vm_size')
    def test_setup_dusty_config_pass_arguments_3(self, fake_get_vm_size, fake_get_mac, fake_get_default_specs, fake_pwnam):
        setup_dusty_config(specs_repo='1')
        fake_get_vm_size.assert_has_calls([call()])
        fake_get_mac.assert_has_calls([call()])
        fake_get_default_specs.assert_has_calls([])

    @patch('dusty.commands.setup.update_managed_repos')
    @patch('dusty.commands.setup.save_config_value')
    def test_complete_setup(self, fake_save_config_value, *args):
        dict_argument = {constants.CONFIG_MAC_USERNAME_KEY: 'user',
                         constants.CONFIG_SPECS_REPO_KEY: 'github.com/gamechanger/dusty'}
        complete_setup(dict_argument)
        fake_save_config_value.assert_has_calls([call(constants.CONFIG_MAC_USERNAME_KEY,'user'),
                                                 call(constants.CONFIG_SPECS_REPO_KEY, 'github.com/gamechanger/dusty'),
                                                 call(constants.CONFIG_SETUP_KEY, True)])

    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.virtual_memory')
    def test_get_boot2docker_vm_size_16_y(self, fake_virtual_memory, fake_get_raw_input):
        total_mock = Mock()
        total_mock.total = 16 * 2**30
        fake_virtual_memory.return_value = total_mock
        fake_get_raw_input.return_value = 'y'
        self.assertEqual(_get_boot2docker_vm_size(), 6144)
        fake_get_raw_input.assert_has_calls([call('Your system seems to have 16384 megabytes of memory. We would like to allocate 6144 to your vm. Is that ok? (y/n) ')])

    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.virtual_memory')
    def test_get_boot2docker_vm_size_16_n(self, fake_virtual_memory, fake_get_raw_input):
        total_mock = Mock()
        total_mock.total = 16 * 2**30
        fake_virtual_memory.return_value = total_mock
        fake_get_raw_input.side_effect = ['n', 2]
        self.assertEqual(_get_boot2docker_vm_size(), 2)
        fake_get_raw_input.assert_has_calls([call('Your system seems to have 16384 megabytes of memory. We would like to allocate 6144 to your vm. Is that ok? (y/n) '),
                                             call('Please input the number of megabytes to allocate to the vm: ')])

    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.virtual_memory')
    def test_get_boot2docker_vm_size_8_y(self, fake_virtual_memory, fake_get_raw_input):
        total_mock = Mock()
        total_mock.total = 8 * 2**30
        fake_virtual_memory.return_value = total_mock
        fake_get_raw_input.return_value = 'y'
        self.assertEqual(_get_boot2docker_vm_size(), 4096)
        fake_get_raw_input.assert_has_calls([call('Your system seems to have 8192 megabytes of memory. We would like to allocate 4096 to your vm. Is that ok? (y/n) ')])

    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.virtual_memory')
    def test_get_boot2docker_vm_size_8_n(self, fake_virtual_memory, fake_get_raw_input):
        total_mock = Mock()
        total_mock.total = 8 * 2**30
        fake_virtual_memory.return_value = total_mock
        fake_get_raw_input.side_effect = ['n', 2]
        self.assertEqual(_get_boot2docker_vm_size(), 2)
        fake_get_raw_input.assert_has_calls([call('Your system seems to have 8192 megabytes of memory. We would like to allocate 4096 to your vm. Is that ok? (y/n) '),
                                             call('Please input the number of megabytes to allocate to the vm: ')])

    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.virtual_memory')
    def test_get_boot2docker_vm_size_less_8_y(self, fake_virtual_memory, fake_get_raw_input):
        total_mock = Mock()
        total_mock.total = 6 * 2**30
        fake_virtual_memory.return_value = total_mock
        fake_get_raw_input.return_value = 'y'
        self.assertEqual(_get_boot2docker_vm_size(), 2048)
        fake_get_raw_input.assert_has_calls([call('Your system seems to have 6144 megabytes of memory. We would like to allocate 2048 to your vm. Is that ok? (y/n) ')])

    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.virtual_memory')
    def test_get_boot2docker_vm_size_less_8_n(self, fake_virtual_memory, fake_get_raw_input):
        total_mock = Mock()
        total_mock.total = 6 * 2**30
        fake_virtual_memory.return_value = total_mock
        fake_get_raw_input.side_effect = ['n', 1]
        self.assertEqual(_get_boot2docker_vm_size(), 1)
        fake_get_raw_input.assert_has_calls([call('Your system seems to have 6144 megabytes of memory. We would like to allocate 2048 to your vm. Is that ok? (y/n) '),
                                             call('Please input the number of megabytes to allocate to the vm: ')])
    @patch('dusty.commands.setup._get_raw_input')
    def test_enter_is_accepted_as_yes(self, fake_get_raw_input):
        fake_get_raw_input.return_value = ''
        setup_dusty_config()
