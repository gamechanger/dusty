import os
import tempfile

from unittest import TestCase
from mock import patch
from nose.tools import nottest

from dusty import constants
from dusty.runner.nginx import _get_nginx_pid, _ensure_nginx_running_with_latest_config

class TestNginxRunner(TestCase):
    def setUp(self):
        self.temp_pid_path = tempfile.mkstemp()[1]
        self.old_pid_path = constants.NGINX_PID_PATH
        constants.NGINX_PID_PATH = self.temp_pid_path
        self.process_id = os.getpid()
        self._write_pid_file(self.process_id)

    def tearDown(self):
        constants.NGINX_PID_PATH = self.old_pid_path

    @nottest
    def _write_pid_file(self, pid):
        with open(self.temp_pid_path, 'w') as f:
            f.write(str(pid))

    def test_get_nginx_pid_when_running(self):
        self.assertEqual(_get_nginx_pid(), self.process_id)

    def test_get_nginx_pid_when_not_running(self):
        self._write_pid_file(99999)
        self.assertFalse(_get_nginx_pid())

    @patch('subprocess.check_call')
    def test_ensure_nginx_running_when_already_running(self, fake_check_call):
        _ensure_nginx_running_with_latest_config()
        fake_check_call.assert_called_once_with(['nginx', '-s', 'reload'])

    @patch('subprocess.check_call')
    def test_ensure_nginx_running_when_not_already_running(self, fake_check_call):
        self._write_pid_file(99999)
        _ensure_nginx_running_with_latest_config()
        fake_check_call.assert_called_once_with(['nginx'])
