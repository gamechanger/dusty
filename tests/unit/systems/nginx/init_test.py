import os
import tempfile

from mock import patch, call
from nose.tools import nottest

from dusty import constants
from dusty.systems.nginx import _ensure_nginx_running_with_latest_config
from ...utils import DustyTestCase

class TestNginxSystem(DustyTestCase):
    @patch('subprocess.check_call')
    def test_ensure_nginx_running_not_running(self, fake_check_call):
        _ensure_nginx_running_with_latest_config()
        fake_check_call.has_calls(call(['nginx', '-s', 'reload']))

    @patch('subprocess.check_call')
    def test_ensure_nginx_running_when_already_running(self, fake_check_call):
        _ensure_nginx_running_with_latest_config()
        fake_check_call.side_effect = Exception("Boom!")
        fake_check_call.has_calls(call(['nginx', '-s', 'reload']), call(['nginx', 'start']))
