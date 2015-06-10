from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestStopCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestStopCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)
        self.run_command('bundles activate busyboxa busyboxa')
        self.run_command('up')

    def test_stop_container(self):
        self.assertContainerRunning('busyboxa')
        self.run_command('stop')
        self.assertContainerIsNotRunning('busyboxa')
        self.assertContainerExists('busyboxa')

    def test_stop_container_with_rm_flag(self):
        self.run_command('restart')
        self.assertContainerRunning('busyboxa')
        self.run_command('stop --rm-containers')
        self.assertContainerIsNotRunning('busyboxa')
        self.assertContainerDoesNotExist('busyboxa')
