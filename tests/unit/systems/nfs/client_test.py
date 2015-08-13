from mock import Mock

from dusty.systems.nfs import client
from ....testcases import DustyTestCase

class TestNFSClient(DustyTestCase):
    def test_mount_args_string(self):
        fake_repo = Mock()
        fake_repo.local_path = '/repo/local/path'
        fake_repo.vm_path = '/persist/repos/remote/path'
        expected_mount_args = '-t nfs -o async,udp,noatime 192.168.59.3:/repo/local/path /persist/repos/remote/path'
        self.assertEqual(expected_mount_args, client._nfs_mount_args_string(fake_repo))
