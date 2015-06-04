import tempfile
import shutil

from ..testcases import DustyTestCase
from dusty.commands.repos import override_repo
from dusty.path import parent_dir, local_repo_path

class TestPath(DustyTestCase):
    def setUp(self):
        super(TestPath, self).setUp()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestPath, self).tearDown()
        shutil.rmtree(self.temp_dir)

    def test_local_repo_path_no_override(self):
        self.assertEqual(local_repo_path('github.com/app/a'),
                         '/etc/dusty/repos/github.com/app/a')

    def test_local_repo_path_with_override(self):
        override_repo('github.com/app/a', self.temp_dir)
        self.assertEqual(local_repo_path('github.com/app/a'), self.temp_dir)

    def test_parent_dir_on_dir(self):
        self.assertEqual(parent_dir('/some/long/dir'), '/some/long')

    def test_parent_dir_on_file(self):
        self.assertEqual(parent_dir('/some/long/dir/file.txt'), '/some/long/dir')

    def test_parent_dir_on_root_dir(self):
        self.assertEqual(parent_dir('/'), '/')
