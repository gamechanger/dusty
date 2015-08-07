import os
import tempfile
import textwrap

import dusty.constants
from dusty.systems.hosts import _dusty_hosts_config, update_hosts_file_from_port_spec
from dusty.systems import config_file
from ....testcases import DustyTestCase

class TestHostsSystem(DustyTestCase):
    def setUp(self):
        super(TestHostsSystem, self).setUp()
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

    def tearDown(self):
        super(TestHostsSystem, self).tearDown()
        os.remove(self.temp_hosts_path)
        dusty.constants.HOSTS_PATH = self.old_hosts_path

    def test_dusty_hosts_config(self):
        result = _dusty_hosts_config(self.test_spec)
        self.assertEqual(result, self.spec_output)

    def test_update_hosts_file_from_port_spec(self):
        update_hosts_file_from_port_spec({'hosts_file': self.test_spec})
        self.assertEqual(config_file.read(dusty.constants.HOSTS_PATH), self.spec_output)
