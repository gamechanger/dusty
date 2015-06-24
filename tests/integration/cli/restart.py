from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestRestartCli(DustyIntegrationTestCase):
    def setUp(self):
        super(TestRestartCli, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=3)
        self.run_command('bundles activate busyboxa busyboxb busyboxc')
