from mock import patch, call

from ..utils import DustyTestCase
from dusty.commands.setup import (_get_mac_username, _get_default_specs_repo, _get_nginx_includes_dir,
                                  setup_dusty_config, save_dusty_config)


class TestSetupCommands(DustyTestCase):
    @patch('dusty.commands.setup.subprocess.check_output')
    @patch('dusty.commands.setup._get_raw_input')
    def test_get_mac_username_false(self, fake_raw_input, fake_check_output):
        fake_raw_input.return_value = 'n'
        fake_check_output.return_value = 'user\n'
        _get_mac_username()
        fake_raw_input.assert_has_calls([call('Is user your mac_username. y or no: '), call('Enter your actual mac_username: ')])
