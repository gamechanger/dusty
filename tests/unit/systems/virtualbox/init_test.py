from mock import patch, call

from dusty.systems.virtualbox import get_host_ip
from ....testcases import DustyTestCase

@patch('dusty.systems.virtualbox.get_vm_hostonly_adapter')
@patch('dusty.systems.virtualbox._get_hostonly_config')
class TestVirtualbox(DustyTestCase):
    def test_get_host_ip_success(self, fake_get_config, fake_get_adapter):
        fake_get_config.return_value = [
            'Name:            vboxnet0',
            'GUID:            786f6276-656e-4074-8000-0a0027000000',
            'DHCP:            Disabled',
            'IPAddress:       192.168.57.1',
            'NetworkMask:     255.255.255.0',
            '',
            'Name:            vboxnet1',
            'GUID:            786f6276-656e-4174-8000-0a0027000001',
            'DHCP:            Disabled',
            'IPAddress:       192.168.59.3',
            'NetworkMask:     255.255.255.0',
            '',
            'Name:            vboxnet2',
            'GUID:            786f6276-656e-4174-8000-0a0027000001',
            'DHCP:            Disabled',
            'IPAddress:       192.168.58.10',
            'NetworkMask:     255.255.255.0',
        ]
        fake_get_adapter.return_value = 'vboxnet1'
        self.assertEqual(get_host_ip(), '192.168.59.3')

    def test_get_host_ip_no_network(self, fake_get_config, fake_get_adapter):
        fake_get_config.return_value = [
            'Name:            vboxnet0',
            'GUID:            786f6276-656e-4074-8000-0a0027000000',
            'DHCP:            Disabled',
            'IPAddress:       192.168.57.1',
            'NetworkMask:     255.255.255.0',
            '',
            'Name:            vboxnet2',
            'GUID:            786f6276-656e-4174-8000-0a0027000001',
            'DHCP:            Disabled',
            'IPAddress:       192.168.59.3',
            'NetworkMask:     255.255.255.0',
        ]
        fake_get_adapter.return_value = 'vboxnet1'
        with self.assertRaises(RuntimeError):
            get_host_ip()

    def test_get_host_ip_no_ipaddress(self, fake_get_config, fake_get_adapter):
        fake_get_config.return_value = [
            'Name:            vboxnet0',
            'GUID:            786f6276-656e-4074-8000-0a0027000000',
            'DHCP:            Disabled',
            'IPAddress:       192.168.57.1',
            'NetworkMask:     255.255.255.0',
            '',
            'Name:            vboxnet1',
            'GUID:            786f6276-656e-4174-8000-0a0027000001',
            'DHCP:            Disabled',
            'NetworkMask:     255.255.255.0',
            '',
            'Name:            vboxnet2',
            'GUID:            786f6276-656e-4174-8000-0a0027000001',
            'DHCP:            Disabled',
            'IPAddress:       192.168.58.10',
            'NetworkMask:     255.255.255.0',
        ]
        fake_get_adapter.return_value = 'vboxnet1'
        with self.assertRaises(RuntimeError):
            get_host_ip()
