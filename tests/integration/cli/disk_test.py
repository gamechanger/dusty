from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestDiskCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestDiskCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)
        self.run_command('bundles activate busyboxa')

    def tearDown(self):
        try:
            self.run_command('stop')
        except Exception:
            pass
        super(TestDiskCLI, self).tearDown()

    def test_disk_inspect(self):
        result = self.run_command('disk inspect')
        self.assertInSameLine(result, 'Usage', '%')

    def test_disk_cleanup_containers(self):
        self.run_command('up')
        self.run_command('stop')
        self.assertContainerExists('busyboxa')
        self.run_command('disk cleanup_containers')
        self.assertContainerDoesNotExist('busyboxa')

    def test_disk_cleanup_images(self):
        self.run_command('up')
        self.run_command('stop')
        self.assertImageExists('busybox:latest')
        self.run_command('disk cleanup_containers')
        self.run_command('disk cleanup_images')
        self.assertImageDoesNotExist('busybox:latest')
