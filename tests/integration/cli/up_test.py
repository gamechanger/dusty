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
        self.assertIn('Updating managed copy of file:///tmp/fake-repo', run_output)
        run_output = self.run_command('up --no-pull')
        self.assertNotIn('Updating managed copy of file:///tmp/fake-repo', run_output)

    # Regression test for https://github.com/gamechanger/dusty/issues/475
    # Concerning commands failing after changing capitalization of specs on
    # case-insensitive host filesystems (like HFS on Mac)
    def test_up_after_app_rename(self):
        self.run_command('up')
        busybox_single_app_bundle_fixture(num_bundles=2, app_name_transformer=lambda x: x.upper())
        self.run_command('up')
        time.sleep(1)
        self.assertContainerRunning('BUSYBOXA')
