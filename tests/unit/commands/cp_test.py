import os
import tempfile

from ...testcases import DustyTestCase
from dusty.commands.cp import _cleanup_path

class TestCpCommands(DustyTestCase):
    def test_cleanup_path_file(self):
        self.temp_file = tempfile.mkstemp()[1]
        with _cleanup_path(self.temp_file):
            pass
        self.assertFalse(os.path.exists(self.temp_file))

    def test_cleanup_path_file_on_error(self):
        self.temp_file = tempfile.mkstemp()[1]
        try:
            with _cleanup_path(self.temp_file):
                raise RuntimeError()
        except:
            pass
        self.assertFalse(os.path.exists(self.temp_file))

    def test_cleanup_path_dir(self):
        self.temp_dir = tempfile.mkdtemp()
        with _cleanup_path(self.temp_dir):
            pass
        self.assertFalse(os.path.exists(self.temp_dir))

    def test_cleanup_path_dir_on_error(self):
        self.temp_dir = tempfile.mkdtemp()
        try:
            with _cleanup_path(self.temp_dir):
                raise RuntimeError()
        except:
            pass
        self.assertFalse(os.path.exists(self.temp_dir))
