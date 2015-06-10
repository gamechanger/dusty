from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestStopCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestStopCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)
        self.run_command('up')

    def test_stop_container(self):
        self.assertContainerRunning('busyboxa')
