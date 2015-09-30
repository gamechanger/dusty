from mock import patch

from ....testcases import DustyTestCase
from dusty.compiler.port_spec import (_docker_compose_port_spec, _nginx_port_spec,
                                      _hosts_file_port_spec, get_port_spec_document,
                                      ReusedHostFullAddress, ReusedContainerPort,
                                      ReusedStreamHostPort)

class TestPortSpecCompiler(DustyTestCase):
    def setUp(self):
        super(TestPortSpecCompiler, self).setUp()
        self.test_host_forwarding_spec_1 = {'container_port': 80, 'host_name': 'local.gc.com', 'host_port': 80, 'type': 'http'}
        self.test_host_forwarding_spec_2 = {'container_port': 8000, 'host_name': 'local.alex.com', 'host_port': 8001, 'type': 'http'}
        self.test_host_forwarding_spec_3 = {'container_port': 22, 'host_name': 'local.ssh.com', 'host_port': 8000, 'type': 'stream'}

    def test_docker_compose_port_spec_1(self):
        self.assertEqual(_docker_compose_port_spec(self.test_host_forwarding_spec_1, '65000'),
            {'in_container_port': '80',
             'mapped_host_port': '65000'})

    def test_docker_compose_port_spec_2(self):
        self.assertEqual(_docker_compose_port_spec(self.test_host_forwarding_spec_2, '65001'),
            {'in_container_port': '8000',
             'mapped_host_port': '65001'})

    def test_docker_compose_port_spec_3(self):
        self.assertEqual(_docker_compose_port_spec(self.test_host_forwarding_spec_3, '65001'),
            {'in_container_port': '22',
             'mapped_host_port': '65001'})

    def test_nginx_port_spec_1(self):
        self.assertEqual(_nginx_port_spec(self.test_host_forwarding_spec_1, '65000', '192.168.5.10'),
            {'proxied_port': '65000',
             'host_address': 'local.gc.com',
             'host_port': '80',
             'type': 'http'})

    def test_nginx_port_spec_2(self):
        self.assertEqual(_nginx_port_spec(self.test_host_forwarding_spec_2, '65001', '192.168.5.10'),
            {'proxied_port': '65001',
             'host_address': 'local.alex.com',
             'host_port': '8001',
             'type': 'http'})

    def test_nginx_port_spec_3(self):
        self.assertEqual(_nginx_port_spec(self.test_host_forwarding_spec_3, '65001', '192.168.5.10'),
            {'proxied_port': '65001',
             'host_address': 'local.ssh.com',
             'host_port': '8000',
             'type': 'stream'})

    def test_hosts_file_port_spec_1(self):
        self.assertEqual(_hosts_file_port_spec('1.1.1.1', self.test_host_forwarding_spec_1),
            {'forwarded_ip': '1.1.1.1',
            'host_address': 'local.gc.com'})

    def test_hosts_file_port_spec_2(self):
        self.assertEqual(_hosts_file_port_spec('1.1.1.1', self.test_host_forwarding_spec_2),
            {'forwarded_ip': '1.1.1.1',
             'host_address': 'local.alex.com'})

    def test_hosts_file_port_spec_3(self):
        self.assertEqual(_hosts_file_port_spec('1.1.1.1', self.test_host_forwarding_spec_3),
            {'forwarded_ip': '1.1.1.1',
             'host_address': 'local.ssh.com'})

    def test_get_port_spec_document_1_app(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 80,
                                                              'container_port': 80,
                                                              'type': 'http'}]}}}
        correct_port_spec = {'docker_compose':{'gcweb':[{'in_container_port': '80',
                                                        'mapped_host_port': '65000'}]},
                             'nginx':[{'proxied_port': '65000',
                                       'host_address': 'local.gc.com',
                                       'host_port': '80',
                                       'type': 'http'}],
                             'hosts_file':[{'forwarded_ip': '192.168.5.10',
                                            'host_address': 'local.gc.com'}]}
        self.assertEqual(get_port_spec_document(expanded_spec, '192.168.5.10'), correct_port_spec)

    def test_get_port_spec_document_2_apps(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 80,
                                                              'container_port': 80,
                                                              'type': 'http'}]},
                                'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gcapi.com',
                                                              'host_port': 8000,
                                                              'container_port': 8001,
                                                              'type': 'http'}]}}}
        correct_port_spec = {'docker_compose':{'gcweb':[{'in_container_port': '80',
                                                        'mapped_host_port': '65001'}],
                                               'gcapi':[{'in_container_port': '8001',
                                                        'mapped_host_port': '65000'}]},
                             'nginx':[{'proxied_port': '65000',
                                       'host_address': 'local.gcapi.com',
                                       'host_port': '8000',
                                       'type': 'http'},
                                      {'proxied_port': '65001',
                                       'host_address': 'local.gc.com',
                                       'host_port': '80',
                                       'type': 'http'}],
                             'hosts_file':[{'forwarded_ip': '192.168.5.10',
                                            'host_address': 'local.gcapi.com'},
                                          {'forwarded_ip': '192.168.5.10',
                                            'host_address': 'local.gc.com'}]}
        self.assertEqual(get_port_spec_document(expanded_spec, '192.168.5.10'), correct_port_spec)

    def test_get_port_spec_document_2_apps_same_host_port(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 80,
                                                              'container_port': 80,
                                                              'type': 'http'}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 8000,
                                                              'container_port': 8001,
                                                              'type': 'http'}]}}}
        correct_port_spec = {'docker_compose':{'gcweb':[{'in_container_port': '80',
                                                        'mapped_host_port': '65001'}],
                                               'gcapi':[{'in_container_port': '8001',
                                                        'mapped_host_port': '65000'}]},
                             'nginx':[{'proxied_port': '65000',
                                       'host_address': 'local.gc.com',
                                       'host_port': '8000',
                                       'type': 'http'},
                                      {'proxied_port': '65001',
                                       'host_address': 'local.gc.com',
                                       'host_port': '80',
                                       'type': 'http'}],
                             'hosts_file':[{'forwarded_ip': '192.168.5.10',
                                            'host_address': 'local.gc.com'}]}
        self.maxDiff = None
        self.assertEqual(get_port_spec_document(expanded_spec, '192.168.5.10'), correct_port_spec)

    def test_port_spec_throws_full_address_error(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 80,
                                                              'container_port': 80,
                                                              'type': 'http'}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 80,
                                                              'container_port': 81,
                                                              'type': 'http'}]}}}
        with self.assertRaises(ReusedHostFullAddress):
            get_port_spec_document(expanded_spec, '192.168.5.10')

    def test_port_spec_throws_container_port(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 80,
                                                              'container_port': 80,
                                                              'type': 'http'},
                                                             {'host_name': 'local.gc.com',
                                                             'host_port': 81,
                                                              'container_port': 80,
                                                              'type': 'http'}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 82,
                                                              'container_port': 81,
                                                              'type': 'http'}]}}}
        with self.assertRaises(ReusedContainerPort):
            get_port_spec_document(expanded_spec, '192.168.5.10')

    def test_port_spec_throws_stream_host_port(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 80,
                                                              'container_port': 80,
                                                              'type': 'stream'}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.api.com',
                                                              'host_port': 80,
                                                              'container_port': 81,
                                                              'type': 'stream'}]}}}
        with self.assertRaises(ReusedStreamHostPort):
            get_port_spec_document(expanded_spec, '192.168.5.10')

    def test_app_with_multiple_host_forwardings(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                              'host_port': 80,
                                                              'container_port': 80,
                                                              'type': 'http'},
                                                             {'host_name': 'local.gc.com',
                                                              'host_port': 81,
                                                              'container_port': 81,
                                                              'type': 'http'}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gcapi.com',
                                                              'host_port': 82,
                                                              'container_port': 82,
                                                              'type': 'http'}]}}}
        correct_port_spec = {'docker_compose':{'gcweb':[{'in_container_port': '80',
                                                        'mapped_host_port': '65001'},
                                                        {'in_container_port': '81',
                                                        'mapped_host_port': '65002'}],
                                               'gcapi':[{'in_container_port': '82',
                                                        'mapped_host_port': '65000'}]},
                             'nginx':[{'proxied_port': '65000',
                                       'host_address': 'local.gcapi.com',
                                       'host_port': '82',
                                       'type': 'http'},
                                      {'proxied_port': '65001',
                                       'host_address': 'local.gc.com',
                                       'host_port': '80',
                                       'type': 'http'},
                                      {'proxied_port': '65002',
                                       'host_address': 'local.gc.com',
                                       'host_port': '81',
                                       'type': 'http'}],
                             'hosts_file':[{'forwarded_ip': '192.168.5.10',
                                            'host_address': 'local.gcapi.com'},
                                           {'forwarded_ip': '192.168.5.10',
                                            'host_address': 'local.gc.com'}]}
        self.assertEqual(get_port_spec_document(expanded_spec, '192.168.5.10'), correct_port_spec)
