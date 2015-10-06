import subprocess
import sys

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestTestCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestTestCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)

    def test_basic_test_run(self):
        result = self.run_command('test --recreate busyboxa test1')
        self.assertEqual(self.handler.log_to_client_output.count('TESTS test1 PASSED'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('OK'), 1)
        self.assertTrue('Running commands to create new image:' in result)

    def test_basic_test_args(self):
        result = self.run_command('test --recreate busyboxa test3')
        self.assertEqual(self.handler.log_to_client_output.count('var\n'), 0)
        self.assertEqual(self.handler.log_to_client_output.count('etc\n'), 0)
        self.assertEqual(self.handler.log_to_client_output.count('sbin\n'), 0)
        self.handler.log_to_client_output = ''

        self.run_command('test --recreate busyboxa test3 /')
        self.assertEqual(self.handler.log_to_client_output.count('var\n'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('etc\n'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('sbin\n'), 1)

    def test_basic_test_all(self):
        result = self.run_command('test --recreate busyboxa all')
        self.assertEqual(self.handler.log_to_client_output.count('TESTS PASSED'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('OK'), 2)
        self.assertTrue('Running commands to create new image:' in result)


    def test_basic_test_no_recreate(self):
        result = self.run_command('test --recreate busyboxa test1')
        self.assertTrue('Running commands to create new image:' in result)
        self.handler.log_to_client_output = ''
        result = self.run_command('test busyboxa test1')
        self.assertFalse('Running commands to create new image:' in result)
        self.assertEqual(self.handler.log_to_client_output.count('TESTS test1 PASSED'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('OK'), 1)
