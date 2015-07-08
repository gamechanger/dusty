import subprocess
import sys

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture
from dusty.log import client_logger, DustyClientTestingSocketHandler

class TestTestCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestTestCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1, include_tests=True)
        self.handler = DustyClientTestingSocketHandler()
        client_logger.addHandler(self.handler)

    def tearDown(self):
        self.handler.log_to_client_output = ''
        client_logger.removeHandler(self.handler)

    def test_basic_test_run(self):
        self.run_command('test --recreate busyboxa test1')
        self.assertEqual(self.handler.log_to_client_output.count('TESTS PASSED'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('OK'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('Running commands to create new image:'), 1)

    def test_basic_test_args(self):
        try:
            self.run_command('test --recreate busyboxa test1 test/location')
        except:
            pass
        self.assertEqual(self.handler.log_to_client_output.count('TESTS FAILED'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('OSError: No such file'), 1)

    def test_basic_test_all(self):
        self.run_command('test --recreate busyboxa all')
        self.assertEqual(self.handler.log_to_client_output.count('TESTS PASSED'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('OK'), 2)
        self.assertEqual(self.handler.log_to_client_output.count('Running commands to create new image:'), 1)

    def test_basic_test_no_recreate(self):
        self.run_command('test --recreate busyboxa test1')
        self.assertEqual(self.handler.log_to_client_output.count('Running commands to create new image:'), 1)
        self.handler.log_to_client_output = ''
        self.run_command('test busyboxa test1')
        self.assertEqual(self.handler.log_to_client_output.count('TESTS PASSED'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('OK'), 1)
        self.assertEqual(self.handler.log_to_client_output.count('Running commands to create new image:'), 0)
