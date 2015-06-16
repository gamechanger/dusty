from mock import patch, call

from ...testcases import DustyTestCase
from dusty.commands.setup import (_get_mac_username, _get_and_configure_nginx_includes_dir,
                                  setup_dusty_config, complete_setup, _setup_nginx_config)
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

    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_conf_yes_servers(self, fake_get_contents, fake_isfile):
        fake_isfile.side_effect = self.factory_file_side_effect('/usr/local/nginx/conf/nginx.conf')
        fake_get_contents.return_value = ['include servers/*;']
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '/usr/local/nginx/conf/servers')

    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_etc_yes_servers(self, fake_get_contents, fake_isfile):
        fake_isfile.side_effect = self.factory_file_side_effect('/etc/nginx/nginx.conf')
        fake_get_contents.return_value = ['include servers/*;']
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '/etc/nginx/servers')

    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_usr_yes_servers(self, fake_get_contents, fake_isfile):
        fake_isfile.side_effect = self.factory_file_side_effect('/usr/local/etc/nginx/nginx.conf')
        fake_get_contents.return_value = ['include servers/*;']
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '/usr/local/etc/nginx/servers')

    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_conf_yes_other(self, fake_get_contents, fake_isfile):
        fake_isfile.side_effect = self.factory_file_side_effect('/usr/local/nginx/conf/nginx.conf')
        fake_get_contents.return_value = ['include real/servers/are/here/*;']
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '/usr/local/nginx/conf/real/servers/are/here')

    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_etc_yes_other(self, fake_get_contents, fake_isfile):
        fake_isfile.side_effect = self.factory_file_side_effect('/etc/nginx/nginx.conf')
        fake_get_contents.return_value = ['include server/*;']
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '/etc/nginx/server')

    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_usr_yes_other(self, fake_get_contents, fake_isfile):
        fake_isfile.side_effect = self.factory_file_side_effect('/usr/local/etc/nginx/nginx.conf')
        fake_get_contents.return_value = ['include two_level/servers/*;']
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '/usr/local/etc/nginx/two_level/servers')

    @patch('dusty.commands.setup._setup_nginx_config')
    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_usr_no_add(self, fake_get_contents, fake_isfile, fake_get_raw_input, fake_setup_nginx):
        fake_isfile.side_effect = self.factory_file_side_effect('/usr/local/etc/nginx/nginx.conf')
        fake_get_contents.return_value = ['servers/*;']
        fake_get_raw_input.return_value = 'y'
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, fake_setup_nginx.return_value)
        fake_setup_nginx.assert_has_calls([call('/usr/local/etc/nginx')])

    @patch('dusty.commands.setup._setup_nginx_config')
    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_etc_no_add(self, fake_get_contents, fake_isfile, fake_get_raw_input, fake_setup_nginx):
        fake_isfile.side_effect = self.factory_file_side_effect('/etc/nginx/nginx.conf')
        fake_get_contents.return_value = ['servers/*;']
        fake_get_raw_input.return_value = 'y'
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, fake_setup_nginx.return_value)
        fake_setup_nginx.assert_has_calls([call('/etc/nginx')])

    @patch('dusty.commands.setup._setup_nginx_config')
    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_conf_no_add(self, fake_get_contents, fake_isfile, fake_get_raw_input, fake_setup_nginx):
        fake_isfile.side_effect = self.factory_file_side_effect('/usr/local/nginx/conf/nginx.conf')
        fake_get_contents.return_value = ['servers/*;']
        fake_get_raw_input.return_value = 'y'
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, fake_setup_nginx.return_value)
        fake_setup_nginx.assert_has_calls([call('/usr/local/nginx/conf')])

    @patch('dusty.commands.setup._setup_nginx_config')
    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_usr_no(self, fake_get_contents, fake_isfile, fake_get_raw_input, fake_setup_nginx):
        fake_isfile.side_effect = self.factory_file_side_effect('/usr/local/etc/nginx/nginx.conf')
        fake_get_contents.return_value = ['servers/*;']
        fake_get_raw_input.return_value = ''
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '')

    @patch('dusty.commands.setup._setup_nginx_config')
    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_etc_no(self, fake_get_contents, fake_isfile, fake_get_raw_input, fake_setup_nginx):
        fake_isfile.side_effect = self.factory_file_side_effect('/etc/nginx/nginx.conf')
        fake_get_contents.return_value = ['servers/*;']
        fake_get_raw_input.return_value = 'n'
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '')

    @patch('dusty.commands.setup._setup_nginx_config')
    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.isfile')
    @patch('dusty.commands.setup._get_contents_of_file')
    def test_get_and_configure_nginx_includes_dir_conf_no(self, fake_get_contents, fake_isfile, fake_get_raw_input, fake_setup_nginx):
        fake_isfile.side_effect = self.factory_file_side_effect('/usr/local/nginx/conf/nginx.conf')
        fake_get_contents.return_value = ['servers/*;']
        fake_get_raw_input.return_value = 'n'
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '')

    @patch('dusty.commands.setup._setup_nginx_config')
    @patch('dusty.commands.setup._get_raw_input')
    @patch('dusty.commands.setup.isfile')
    def test_get_and_configure_nginx_includes_dir_none(self, fake_isfile, fake_get_raw_input, fake_setup_nginx):
        fake_isfile.side_effect = self.factory_file_side_effect('')
        fake_get_raw_input.return_value = '/usr/local/nginx/conf/servers'
        result = _get_and_configure_nginx_includes_dir()
        self.assertEqual(result, '/usr/local/nginx/conf/servers')

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_and_configure_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config(self, fake_get_mac, fake_get_default_specs, fake_get_nginx, fake_pwnam):
        fake_get_mac.return_value = 'user'
        fake_get_default_specs.return_value = 'github.com/gamechanger/dusty'
        fake_get_nginx.return_value = '/etc/dusty/nginx'
        expected_dict_argument = {constants.CONFIG_MAC_USERNAME_KEY: 'user',
                                  constants.CONFIG_SPECS_REPO_KEY: 'github.com/gamechanger/dusty',
                                  constants.CONFIG_NGINX_DIR_KEY: '/etc/dusty/nginx'}
        return_payload = setup_dusty_config()
        self.assertEqual(return_payload.fn, complete_setup)
        self.assertEqual(return_payload.args[0], expected_dict_argument)

    @patch('dusty.commands.setup.isdir')
    @patch('dusty.commands.setup.mkdir')
    @patch('dusty.commands.setup._append_to_file')
    def test_setup_nginx_config_no_dir(self, fake_append, fake_mkdir, fake_isdir):
        fake_isdir.return_value = False
        _setup_nginx_config('/usr/local/etc/nginx')
        fake_mkdir.assert_has_calls([call('/usr/local/etc/nginx/servers')])
        fake_append.assert_has_calls([call('/usr/local/etc/nginx/nginx.conf', '\ninclude servers/*;\n')])

    @patch('dusty.commands.setup.isdir')
    @patch('dusty.commands.setup.mkdir')
    @patch('dusty.commands.setup._append_to_file')
    def test_setup_nginx_config_dir(self, fake_append, fake_mkdir, fake_isdir):
        fake_isdir.return_value = True
        _setup_nginx_config('/usr/local/etc/nginx')
        fake_mkdir.assert_has_calls([])
        fake_append.assert_has_calls([call('/usr/local/etc/nginx/nginx.conf', '\ninclude servers/*;\n')])

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_and_configure_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config_pass_arguments_1(self, fake_get_mac, fake_get_default_specs, fake_get_nginx, fake_pwnam):
        setup_dusty_config(mac_username='1',
                           specs_repo='2',
                           nginx_includes_dir='3')
        fake_get_mac.assert_has_calls([])
        fake_get_default_specs.assert_has_calls([])
        fake_get_nginx.assert_has_calls([])

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_and_configure_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config_pass_arguments_2(self, fake_get_mac, fake_get_default_specs, fake_get_nginx, fake_pwnam):
        setup_dusty_config(mac_username='1')
        fake_get_mac.assert_has_calls([])
        fake_get_default_specs.assert_has_calls([call()])
        fake_get_nginx.assert_has_calls([call()])

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_and_configure_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config_pass_arguments_3(self, fake_get_mac, fake_get_default_specs, fake_get_nginx, fake_pwnam):
        setup_dusty_config(specs_repo='1')
        fake_get_mac.assert_has_calls([call()])
        fake_get_default_specs.assert_has_calls([])
        fake_get_nginx.assert_has_calls([call()])

    @patch('pwd.getpwnam')
    @patch('dusty.commands.setup._get_and_configure_nginx_includes_dir')
    @patch('dusty.commands.setup._get_default_specs_repo')
    @patch('dusty.commands.setup._get_mac_username')
    def test_setup_dusty_config_pass_arguments_4(self, fake_get_mac, fake_get_default_specs, fake_get_nginx, fake_pwnam):
        setup_dusty_config(nginx_includes_dir='1')
        fake_get_mac.assert_has_calls([call()])
        fake_get_default_specs.assert_has_calls([call()])
        fake_get_nginx.assert_has_calls([])

    @patch('dusty.commands.setup.save_config_value')
    def test_complete_setup(self, fake_save_config_value):
        dict_argument = {constants.CONFIG_MAC_USERNAME_KEY: 'user',
                         constants.CONFIG_SPECS_REPO_KEY: 'github.com/gamechanger/dusty',
                         constants.CONFIG_NGINX_DIR_KEY: '/etc/dusty/nginx'}
        complete_setup(dict_argument)
        fake_save_config_value.assert_has_calls([call(constants.CONFIG_MAC_USERNAME_KEY,'user'),
                                                 call(constants.CONFIG_SPECS_REPO_KEY, 'github.com/gamechanger/dusty'),
                                                 call(constants.CONFIG_NGINX_DIR_KEY, '/etc/dusty/nginx'),
                                                 call(constants.CONFIG_SETUP_KEY, True)])
