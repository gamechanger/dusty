import os
import tempfile

from mock import patch
from nose.tools import nottest

from dusty import constants
from dusty.systems.nginx import _ensure_nginx_running_with_latest_config
from ...utils import DustyTestCase

class TestNginxSystem(DustyTestCase):
    @patch('subprocess.call')
    @patch('subprocess.check_call')
    def test_ensure_nginx_running_when_already_running(self, fake_check_call, fake_call):
        _ensure_nginx_running_with_latest_config()
        fake_call.assert_called_once_with(['nginx', '-s', 'stop'])
        fake_check_call.assert_called_once_with(['nginx'])
