import os
import tempfile

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestCpCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestCpCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)
        self.run_command('bundles activate busyboxa')

        self.file_paths = []
        self.temp_dir = tempfile.mkdtemp()
        for file_num in range(1, 3):
            file_path = os.path.join(self.temp_dir, 'file{}.txt'.format(file_num))
            self.file_paths.append(file_path)
            with open(file_path, 'w') as f:
                f.write('contents{}'.format(file_num))

    def test_cp_file_from_local_to_container(self):
        self.run_command('up')
        self.run_command('cp {} busyboxa:/new-folder/file1.txt'.format(self.file_paths[0]))
        self.assertFileContentsInContainer('busyboxa',
                                           '/new-folder/file1.txt',
                                           'contents1')
