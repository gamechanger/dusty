import os
import tempfile

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestCpCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestCpCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=2)
        self.run_command('bundles activate busyboxa busyboxb')
        self.file_paths = []
        self.temp_dir = tempfile.mkdtemp()
        os.chmod(self.temp_dir, 0777)
        for file_num in range(1, 3):
            file_path = os.path.join(self.temp_dir, 'file{}.txt'.format(file_num))
            self.file_paths.append(file_path)
            with open(file_path, 'w') as f:
                f.write('contents{}'.format(file_num))

        self.run_command('up')

    def tearDown(self):
        self.run_command('stop')
        super(TestCpCLI, self).tearDown()

    def test_cp_file_from_local_to_container(self):
        self.run_command('cp {} busyboxa:/new-folder/file1.txt'.format(self.file_paths[0]))
        self.assertFileContentsInContainer('busyboxa',
                                           '/new-folder/file1.txt',
                                           'contents1')

    def test_cp_file_from_local_to_container_when_folder_exists(self):
        self.exec_in_container('busyboxa', 'mkdir -p /new-folder')
        self.run_command('cp {} busyboxa:/new-folder/file1.txt'.format(self.file_paths[0]))
        self.assertFileContentsInContainer('busyboxa',
                                           '/new-folder/file1.txt',
                                           'contents1')

    def test_cp_dir_from_local_to_container(self):
        self.run_command('cp {} busyboxa:/new-folder'.format(self.temp_dir))
        self.assertFileContentsInContainer('busyboxa',
                                           'new-folder/file1.txt',
                                           'contents1')
        self.assertFileContentsInContainer('busyboxa',
                                           'new-folder/file2.txt',
                                           'contents2')

    def test_cp_dir_from_local_to_container_when_folder_exists(self):
        self.exec_in_container('busyboxa', 'mkdir -p /new-folder')
        self.run_command('cp {} busyboxa:/new-folder'.format(self.temp_dir))
        self.assertFileContentsInContainer('busyboxa',
                                           'new-folder/file1.txt',
                                           'contents1')
        self.assertFileContentsInContainer('busyboxa',
                                           'new-folder/file2.txt',
                                           'contents2')

    def test_cp_file_from_container_to_local(self):
        self.write_file_in_container('busyboxa', '/output.txt', 'contents')
        target = os.path.join(self.temp_dir, 'output.txt')
        self.run_command('cp busyboxa:/output.txt {}'.format(target))
        self.assertFileContents(target, 'contents')

    def test_cp_dir_from_container_to_local(self):
        self.remove_path_in_container('busyboxa', '/output')
        self.write_file_in_container('busyboxa', '/output/file1.txt', '1')
        self.write_file_in_container('busyboxa', '/output/file2.txt', '2')
        target = os.path.join(self.temp_dir, 'output')
        self.run_command('cp busyboxa:/output {}'.format(target))
        self.assertFileContents(os.path.join(target, 'file1.txt'), '1')
        self.assertFileContents(os.path.join(target, 'file2.txt'), '2')

    def test_cp_file_between_containers(self):
        self.write_file_in_container('busyboxa', '/output.txt', 'contents')
        self.run_command('cp busyboxa:/output.txt busyboxb:/output.txt')
        self.assertFileContentsInContainer('busyboxb', '/output.txt', 'contents')

    def test_cp_file_between_containers_when_target_exists(self):
        self.write_file_in_container('busyboxa', '/output.txt', 'changed')
        self.write_file_in_container('busyboxb', '/output.txt', 'original')
        self.run_command('cp busyboxa:/output.txt busyboxb:/output.txt')
        self.assertFileContentsInContainer('busyboxb', '/output.txt', 'changed')

    def test_cp_dir_between_containers(self):
        self.remove_path_in_container('busyboxa', '/output')
        self.write_file_in_container('busyboxa', '/output/file1.txt', '1')
        self.write_file_in_container('busyboxa', '/output/file2.txt', '2')
        self.run_command('cp busyboxa:/output busyboxb:/output')
        self.assertFileContentsInContainer('busyboxb', '/output/file1.txt', '1')
        self.assertFileContentsInContainer('busyboxb', '/output/file2.txt', '2')
