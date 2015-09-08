import os
import tempfile

from mock import patch

import dusty.constants
from dusty.systems.known_hosts import ensure_known_hosts
from ....testcases import DustyTestCase

@patch('dusty.systems.known_hosts._get_known_hosts_path')
@patch('dusty.systems.known_hosts.check_output')
class TestKnownHostsSystem(DustyTestCase):
    def setUp(self):
        super(TestKnownHostsSystem, self).setUp()
        self.temp_hosts_path = tempfile.mkstemp()[1]

    def tearDown(self):
        super(TestKnownHostsSystem, self).tearDown()
        os.remove(self.temp_hosts_path)

    def test_preserves_existing_content(self, fake_check_output, fake_get_known_hosts):
        fake_get_known_hosts.return_value = self.temp_hosts_path
        fake_check_output.return_value = 'dusty.host:SOMESHA'

        initial_content = 'prev.known.host.1:SOMESHA\nprev.known.host.2:SOMESHA'
        with open(self.temp_hosts_path, 'w') as f:
            f.write(initial_content)
        expected_result_content = 'prev.known.host.1:SOMESHA\nprev.known.host.2:SOMESHA\ndusty.host:SOMESHA'

        ensure_known_hosts(['dusty.host'])
        with open(self.temp_hosts_path, 'r') as f:
            self.assertEqual(f.read(), expected_result_content)

    def test_not_modified(self, fake_check_output, fake_get_known_hosts):
        fake_get_known_hosts.return_value = self.temp_hosts_path
        fake_check_output.return_value = 'prev.known.host.1:SOMESHA'

        initial_content = 'prev.known.host.1:SOMESHA\nprev.known.host.2:SOMESHA'
        with open(self.temp_hosts_path, 'w') as f:
            f.write(initial_content)

        ensure_known_hosts(['prev.known.host.1'])
        with open(self.temp_hosts_path, 'r') as f:
            self.assertEqual(f.read(), initial_content)

    def test_redundant_additions(self, fake_check_output, fake_get_known_hosts):
        fake_get_known_hosts.return_value = self.temp_hosts_path
        fake_check_output.return_value = 'dusty.host:SOMESHA'

        initial_content = 'prev.known.host.1:SOMESHA\nprev.known.host.2:SOMESHA'
        with open(self.temp_hosts_path, 'w') as f:
            f.write(initial_content)
        expected_result_content = 'prev.known.host.1:SOMESHA\nprev.known.host.2:SOMESHA\ndusty.host:SOMESHA'

        ensure_known_hosts(['dusty.host', 'dusty.host', 'dusty.host'])
        with open(self.temp_hosts_path, 'r') as f:
            self.assertEqual(f.read(), expected_result_content)
