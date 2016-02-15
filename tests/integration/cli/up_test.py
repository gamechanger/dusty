import time
import subprocess

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestUpCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestUpCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=2)
        self.run_command('bundles activate busyboxa busyboxb')

    def tearDown(self):
        try:
            self.run_command('stop')
        except Exception:
            pass
        super(TestUpCLI, self).tearDown()

    def test_basic_up_command(self):
        run_output = self.run_command('up')
        self.assertIn('Your local environment is now started!', run_output)
        self.assertContainerRunning('busyboxa')
        self.assertContainerRunning('busyboxb')

    def test_basic_up_recreate(self):
        run_output = self.run_command('up')
        run_output = self.run_command('up')
        self.assertIn('Removing dusty_busyboxb_1', run_output)
        self.assertIn('Removing dusty_busyboxa_1', run_output)
        self.assertIn('Creating dusty_busyboxb_1', run_output)
        self.assertIn('Creating dusty_busyboxa_1', run_output)
        run_output = self.run_command('up --no-recreate')
        self.assertNotIn('Creating dusty_busyboxb_1', run_output)
        self.assertNotIn('Creating dusty_busyboxa_1', run_output)

    def test_basic_up_no_pull(self):
        run_output = self.run_command('up')
        self.assertIn('Updated managed copy of file:///tmp/fake-repo', run_output)
        run_output = self.run_command('up --no-pull')
        self.assertNotIn('Updated managed copy of file:///tmp/fake-repo', run_output)
