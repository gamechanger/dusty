import os
import subprocess
import tempfile

from mock import patch

from ...testcases import DustyTestCase
from dusty.commands.upgrade import _move_temp_binary_to_path

class UpgradeTestCase(DustyTestCase):
    def setUp(self):
        super(UpgradeTestCase, self).setUp()
        self.file1_path = tempfile.mkstemp(suffix='dusty')[1]
        self.file2_path = tempfile.mkstemp(suffix='dusty')[1]


    @patch('dusty.commands.upgrade._get_binary_location')
    def test_move_preserves_permissions(self, fake_get_binary_location):
        os.chmod(self.file1_path, 0764)
        os.chmod(self.file2_path, 0777)
        previous_st_mode = os.stat(self.file1_path).st_mode
        fake_get_binary_location.return_value = self.file1_path
        _move_temp_binary_to_path(self.file2_path)
        self.assertEqual(os.stat(self.file1_path).st_mode, previous_st_mode)

    @patch('dusty.commands.upgrade._get_binary_location')
    def test_refuses_to_overwrite(self, fake_get_binary_location):
        fake_get_binary_location.return_value = self.file1_path.rstrip('dusty')
        with self.assertRaises(RuntimeError):
            _move_temp_binary_to_path(self.file2_path)
