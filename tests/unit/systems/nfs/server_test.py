import os
import tempfile

from mock import Mock, patch

from dusty.systems.nfs import server
from dusty import constants
from ....testcases import DustyTestCase

class TestNFSServer(DustyTestCase):
    def setUp(self):
        super(TestNFSServer, self).setUp()

    def tearDown(self):
        super(TestNFSServer, self).tearDown()

    @patch('dusty.systems.config_file.get_dusty_config_section')
    def test_get_current_exports(self, fake_get_dusty_config_section):
        fake_get_dusty_config_section.return_value = 'export numba 1\n/private/etc/some/repo 192.168.59.103 -alldirs -maproot=0:0\n'
        expected_current_exports = set(['export numba 1\n', '/private/etc/some/repo 192.168.59.103 -alldirs -maproot=0:0\n'])
        self.assertEqual(expected_current_exports, server._get_current_exports())

    def test_maproot_for_repo(self):
        fake_repo = Mock()
        fake_repo.local_path = tempfile.mkdtemp()
        expected_maproot = '{}:{}'.format(os.stat(fake_repo.local_path).st_uid, os.stat(fake_repo.local_path).st_gid)
        self.assertEqual(expected_maproot, server._maproot_for_repo(fake_repo))

    def test_write_exports_config(self):
        exports_set = set(['export1\n', 'export2\n'])
        constants.EXPORTS_PATH = tempfile.mkstemp()[1]

