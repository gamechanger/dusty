from mock import patch, call

from ..utils import DustyTestCase
from dusty.commands.setup import (_get_mac_username, _get_nginx_includes_dir,
                                  setup_dusty_config, save_dusty_config)
from dusty.payload import Payload
from dusty import constants

class TestSetupCommands(DustyTestCase):
    @patch('dusty.commands.setup.subprocess.check_output')
    @patch('dusty.commands.setup._get_raw_input')
    def test_get_mac_username_no(self, fake_raw_input, fake_check_output):
        fake_raw_input.return_value = 'n'
        fake_check_output.return_value = 'user\n'
        _get_mac_username()
        fake_raw_input.assert_has_calls([call('Is user your mac_username. y or no: '), call('Enter your actual mac_username: ')])

    @patch('dusty.commands.setup.subprocess.check_output')
    @patch('dusty.commands.setup._get_raw_input')
    def test_get_mac_username_yes(self, fake_raw_input, fake_check_output):
        fake_raw_input.return_value = 'y'
        fake_check_output.return_value = 'user\n'
        _get_mac_username()
        fake_raw_input.assert_has_calls([call('Is user your mac_username. y or no: ')])

    @patch('dusty.commands.setup.get_config_value')
    @patch('dusty.commands.setup._get_raw_input')
    def test_get_nginx_includes_dir_no(self, fake_raw_input, fake_get_config_value):
        fake_raw_input.return_value = 'n'
        fake_get_config_value.return_value = '/etc/dusty/nginx'
        _get_nginx_includes_dir()
        fake_raw_input.assert_has_calls([call('Does your nginx config look for extra configs in the default location of /etc/dusty/nginx. y or n: '),
                                         call('Please input the path where your nginx config pulls extra configs: ')])

    @patch('dusty.commands.setup.get_config_value')
    @patch('dusty.commands.setup._get_raw_input')
    def test_get_nginx_includes_dir_yes(self, fake_raw_input, fake_get_config_value):
        fake_raw_input.return_value = 'y'
        fake_get_config_value.return_value = '/etc/dusty/nginx'
        _get_nginx_includes_dir()
        fake_raw_input.assert_has_calls([call('Does your nginx config look for extra configs in the default location of /etc/dusty/nginx. y or n: ')])


    @patch('dusty.commands.setup._get_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config(self, fake_get_mac, fake_get_default_specs, fake_get_nginx):
        fake_get_mac.return_value = 'user'
        fake_get_default_specs.return_value = 'github.com/gamechanger/dusty'
        fake_get_nginx.return_value = '/etc/dusty/nginx'
        expected_dict_argument = {constants.CONFIG_MAC_USERNAME_KEY: 'user',
                                  constants.CONFIG_SPECS_REPO_KEY: 'github.com/gamechanger/dusty',
                                  constants.CONFIG_NGINX_DIR_KEY: '/etc/dusty/nginx'}
        return_payload = setup_dusty_config()
        self.assertEqual(return_payload.fn, save_dusty_config)
        self.assertEqual(return_payload.args[0], expected_dict_argument)

    @patch('dusty.commands.setup._get_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config_pass_arguments_1(self, fake_get_mac, fake_get_default_specs, fake_get_nginx):
        setup_dusty_config(mac_username='1',
                           specs_repo='2',
                           nginx_includes_dir='3')
        fake_get_mac.assert_has_calls([])
        fake_get_default_specs.assert_has_calls([])
        fake_get_nginx.assert_has_calls([])

    @patch('dusty.commands.setup._get_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config_pass_arguments_2(self, fake_get_mac, fake_get_default_specs, fake_get_nginx):
        setup_dusty_config(mac_username='1')
        fake_get_mac.assert_has_calls([])
        fake_get_default_specs.assert_has_calls([call()])
        fake_get_nginx.assert_has_calls([call()])

    @patch('dusty.commands.setup._get_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config_pass_arguments_3(self, fake_get_mac, fake_get_default_specs, fake_get_nginx):
        setup_dusty_config(specs_repo='1')
        fake_get_mac.assert_has_calls([call()])
        fake_get_default_specs.assert_has_calls([])
        fake_get_nginx.assert_has_calls([call()])

    @patch('dusty.commands.setup._get_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config_pass_arguments_4(self, fake_get_mac, fake_get_default_specs, fake_get_nginx):
        setup_dusty_config(nginx_includes_dir='1')
        fake_get_mac.assert_has_calls([call()])
        fake_get_default_specs.assert_has_calls([call()])
        fake_get_nginx.assert_has_calls([])

    @patch('dusty.commands.setup.save_config_value')
    def test_save_dusty_config(self, fake_save_config_value):
        dict_argument = {constants.CONFIG_MAC_USERNAME_KEY: 'user',
                         constants.CONFIG_SPECS_REPO_KEY: 'github.com/gamechanger/dusty',
                         constants.CONFIG_NGINX_DIR_KEY: '/etc/dusty/nginx'}
        save_dusty_config(dict_argument)
        fake_save_config_value.assert_has_calls([call(constants.CONFIG_MAC_USERNAME_KEY,'user'),
                                                 call(constants.CONFIG_SPECS_REPO_KEY, 'github.com/gamechanger/dusty'),
                                                 call(constants.CONFIG_NGINX_DIR_KEY, '/etc/dusty/nginx'),
                                                 call(constants.CONFIG_SETUP_KEY, True)])


