from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestStopCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestStopCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=3)
        self.run_command('bundles activate busyboxa busyboxb busyboxc')
        self.run_command('up')

    def tearDown(self):
        try:
            self.run_command('stop')
        except Exception:
            pass
        super(TestStopCLI, self).tearDown()

    def test_stop_container(self):
        self.assertContainerRunning('busyboxa')
        self.run_command('stop')
        self.assertContainerIsNotRunning('busyboxa')
        self.assertContainerExists('busyboxa')

    def test_stop_container_with_rm_flag(self):
        self.assertContainerRunning('busyboxa')
        self.run_command('stop --rm')
        self.assertContainerIsNotRunning('busyboxa')
        self.assertContainerDoesNotExist('busyboxa')

    def test_stop_only_one(self):
        self.assertContainerRunning('busyboxa')
        self.assertContainerRunning('busyboxb')
        self.run_command('stop busyboxa')
        self.assertContainerIsNotRunning('busyboxa')
        self.assertContainerRunning('busyboxb')

    def test_stop_multiple_but_not_all(self):
        self.assertContainerRunning('busyboxa')
        self.assertContainerRunning('busyboxb')
        self.assertContainerRunning('busyboxc')
        self.run_command('stop busyboxa busyboxb')
        self.assertContainerIsNotRunning('busyboxa')
        self.assertContainerIsNotRunning('busyboxb')
        self.assertContainerRunning('busyboxc')

    def test_stop_with_rm(self):
        self.assertContainerRunning('busyboxa')
        self.run_command('stop --rm busyboxa')
        self.assertContainerDoesNotExist('busyboxa')

    def test_stop_multiple_but_not_all_with_rm(self):
        self.assertContainerRunning('busyboxa')
        self.assertContainerRunning('busyboxb')
        self.assertContainerRunning('busyboxc')
        self.run_command('stop --rm busyboxa busyboxb')
        self.assertContainerDoesNotExist('busyboxa')
        self.assertContainerDoesNotExist('busyboxb')
        self.assertContainerRunning('busyboxc')
