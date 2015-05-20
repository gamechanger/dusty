import os
import tempfile
import textwrap

from unittest import TestCase

import dusty.constants
from dusty.systems.hosts import (_remove_current_dusty_config, _dusty_hosts_config,
                                update_hosts_file_from_port_spec, _read_hosts)

class TestHostsRunner(TestCase):
    def setUp(self):
        self.temp_hosts_path = tempfile.mkstemp()[1]
        self.old_hosts_path = dusty.constants.HOSTS_PATH
        dusty.constants.HOSTS_PATH = self.temp_hosts_path
        self.test_spec = [{'host_address': 'local.gc.com', 'forwarded_ip': '127.0.0.1'},
                          {'host_address': 'local-api.gc.com', 'forwarded_ip': '127.0.0.2'}]
        self.spec_output = textwrap.dedent("""\
        # BEGIN section for Dusty
        127.0.0.1 local.gc.com
        127.0.0.2 local-api.gc.com
        # END section for Dusty
        """)
        self.non_spec_starter = "127.0.0.1 some-host.local.com\n"

    def tearDown(self):
        os.remove(self.temp_hosts_path)
        dusty.constants.HOSTS_PATH = self.old_hosts_path

    def test_dusty_hosts_config(self):
        result = _dusty_hosts_config(self.test_spec)
        self.assertEqual(result, self.spec_output)

    def test_remove_current_dusty_config_from_blank(self):
        result = _remove_current_dusty_config(self.spec_output)
        self.assertEqual(result, "")

    def test_remove_current_dusty_config_from_starting(self):
        result = _remove_current_dusty_config(self.non_spec_starter + self.spec_output)
        self.assertEqual(result, self.non_spec_starter)

    def test_update_hosts_file_from_port_spec(self):
        update_hosts_file_from_port_spec({'hosts_file': self.test_spec})
        self.assertEqual(_read_hosts(dusty.constants.HOSTS_PATH), self.spec_output)
