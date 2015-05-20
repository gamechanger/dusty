from unittest import TestCase
from dusty.compiler.port_spec import (_docker_compose_port_spec, _virtualbox_port_spec, _nginx_port_spec,
                                      _hosts_file_port_spec, get_port_spec_document, LOCALHOST,
                                      ReusedHostFullAddress, ReusedContainerPort)

class TestPortSpecCompiler(TestCase):
    def setUp(self):
        self.test_host_forwarding_spec_1 = {'container_port': 80, 'host_name': 'local.gc.com', 'host_port': 80}
        self.test_host_forwarding_spec_2 = {'container_port': 8000, 'host_name': 'local.alex.com', 'host_port': 8001}

    def test_docker_compose_port_spec_1(self):
        self.assertEqual(_docker_compose_port_spec(self.test_host_forwarding_spec_1, '65000'),
            {'in_container_port': '80',
             'mapped_host_ip': LOCALHOST,
             'mapped_host_port': '65000'})

    def test_docker_compose_port_spec_2(self):
        self.assertEqual(_docker_compose_port_spec(self.test_host_forwarding_spec_2, '65001'),
            {'in_container_port': '8000',
             'mapped_host_ip': LOCALHOST,
             'mapped_host_port': '65001'})

    def test_virtualbox_port_spec(self):
        self.assertEqual(_virtualbox_port_spec('65000'),
            {'guest_ip': LOCALHOST,
             'guest_port': '65000',
             'host_ip': LOCALHOST,
             'host_port': '65000'})

    def test_nginx_port_spec_1(self):
        self.assertEqual(_nginx_port_spec(self.test_host_forwarding_spec_1, '65000'),
            {'proxied_ip': LOCALHOST,
             'proxied_port': '65000',
             'host_address': 'local.gc.com',
             'host_port': '80'})

    def test_nginx_port_spec_2(self):
        self.assertEqual(_nginx_port_spec(self.test_host_forwarding_spec_2, '65001'),
            {'proxied_ip': LOCALHOST,
             'proxied_port': '65001',
             'host_address': 'local.alex.com',
             'host_port': '8001'})

    def test_hosts_file_port_spec_1(self):
        self.assertEqual(_hosts_file_port_spec(self.test_host_forwarding_spec_1),
            {'forwarded_ip': LOCALHOST,
            'host_address': 'local.gc.com'})

    def test_hosts_file_port_spec_2(self):
        self.assertEqual(_hosts_file_port_spec(self.test_host_forwarding_spec_2),
            {'forwarded_ip': LOCALHOST,
             'host_address': 'local.alex.com'})

    def test_get_port_spec_document_1_app(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 80,
                                                             'container_port': 80}]}}}
        correct_port_spec = {'docker_compose':{'gcweb':[{'in_container_port': '80',
                                                        'mapped_host_ip': LOCALHOST,
                                                        'mapped_host_port': '65000'}]},
                             'virtualbox':[{'guest_ip': LOCALHOST,
                                            'guest_port': '65000',
                                            'host_ip': LOCALHOST,
                                            'host_port': '65000'}],
                             'nginx':[{'proxied_ip': LOCALHOST,
                                       'proxied_port': '65000',
                                       'host_address': 'local.gc.com',
                                       'host_port': '80'}],
                             'hosts_file':[{'forwarded_ip': LOCALHOST,
                                            'host_address': 'local.gc.com'}]}
        self.assertEqual(get_port_spec_document(expanded_spec), correct_port_spec)

    def test_get_port_spec_document_2_apps(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 80,
                                                             'container_port': 80}]},
                                'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gcapi.com',
                                                             'host_port': 8000,
                                                             'container_port': 8001}]}}}
        correct_port_spec = {'docker_compose':{'gcweb':[{'in_container_port': '80',
                                                        'mapped_host_ip': LOCALHOST,
                                                        'mapped_host_port': '65001'}],
                                               'gcapi':[{'in_container_port': '8001',
                                                        'mapped_host_ip': LOCALHOST,
                                                        'mapped_host_port': '65000'}]},
                             'virtualbox':[{'guest_ip': LOCALHOST,
                                            'guest_port': '65000',
                                            'host_ip': LOCALHOST,
                                            'host_port': '65000'},
                                           {'guest_ip': LOCALHOST,
                                            'guest_port': '65001',
                                            'host_ip': LOCALHOST,
                                            'host_port': '65001'}],
                             'nginx':[{'proxied_ip': LOCALHOST,
                                       'proxied_port': '65000',
                                       'host_address': 'local.gcapi.com',
                                       'host_port': '8000'},
                                      {'proxied_ip': LOCALHOST,
                                       'proxied_port': '65001',
                                       'host_address': 'local.gc.com',
                                       'host_port': '80'}],
                             'hosts_file':[{'forwarded_ip': LOCALHOST,
                                            'host_address': 'local.gcapi.com'},
                                          {'forwarded_ip': LOCALHOST,
                                            'host_address': 'local.gc.com'}]}
        self.assertEqual(get_port_spec_document(expanded_spec), correct_port_spec)

    def test_get_port_spec_document_2_apps_same_host_port(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 80,
                                                             'container_port': 80}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 8000,
                                                             'container_port': 8001}]}}}
        correct_port_spec = {'docker_compose':{'gcweb':[{'in_container_port': '80',
                                                        'mapped_host_ip': LOCALHOST,
                                                        'mapped_host_port': '65001'}],
                                               'gcapi':[{'in_container_port': '8001',
                                                        'mapped_host_ip': LOCALHOST,
                                                        'mapped_host_port': '65000'}]},
                             'virtualbox':[{'guest_ip': LOCALHOST,
                                            'guest_port': '65000',
                                            'host_ip': LOCALHOST,
                                            'host_port': '65000'},
                                           {'guest_ip': LOCALHOST,
                                            'guest_port': '65001',
                                            'host_ip': LOCALHOST,
                                            'host_port': '65001'}],
                             'nginx':[{'proxied_ip': LOCALHOST,
                                       'proxied_port': '65000',
                                       'host_address': 'local.gc.com',
                                       'host_port': '8000'},
                                      {'proxied_ip': LOCALHOST,
                                       'proxied_port': '65001',
                                       'host_address': 'local.gc.com',
                                       'host_port': '80'}],
                             'hosts_file':[{'forwarded_ip': LOCALHOST,
                                            'host_address': 'local.gc.com'}]}
        self.assertEqual(get_port_spec_document(expanded_spec), correct_port_spec)

    def test_port_spec_throws_full_address_error(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 80,
                                                             'container_port': 80}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 80,
                                                             'container_port': 81}]}}}
        with self.assertRaises(ReusedHostFullAddress):
            get_port_spec_document(expanded_spec)

    def test_port_spec_throws_container_port(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 80,
                                                             'container_port': 80},
                                                             {'host_name': 'local.gc.com',
                                                             'host_port': 81,
                                                             'container_port': 80}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 82,
                                                             'container_port': 81}]}}}
        with self.assertRaises(ReusedContainerPort):
            get_port_spec_document(expanded_spec)

    def test_app_with_multiple_host_forwardings(self):
        expanded_spec = {'apps':
                                {'gcweb':
                                         {'host_forwarding':[{'host_name': 'local.gc.com',
                                                             'host_port': 80,
                                                             'container_port': 80},
                                                             {'host_name': 'local.gc.com',
                                                             'host_port': 81,
                                                             'container_port': 81}]},
                                 'gcapi':
                                         {'host_forwarding':[{'host_name': 'local.gcapi.com',
                                                             'host_port': 82,
                                                             'container_port': 82}]}}}
        correct_port_spec = {'docker_compose':{'gcweb':[{'in_container_port': '80',
                                                        'mapped_host_ip': LOCALHOST,
                                                        'mapped_host_port': '65001'},
                                                        {'in_container_port': '81',
                                                        'mapped_host_ip': LOCALHOST,
                                                        'mapped_host_port': '65002'}],
                                               'gcapi':[{'in_container_port': '82',
                                                        'mapped_host_ip': LOCALHOST,
                                                        'mapped_host_port': '65000'}]},
                             'virtualbox':[{'guest_ip': LOCALHOST,
                                            'guest_port': '65000',
                                            'host_ip': LOCALHOST,
                                            'host_port': '65000'},
                                           {'guest_ip': LOCALHOST,
                                            'guest_port': '65001',
                                            'host_ip': LOCALHOST,
                                            'host_port': '65001'},
                                           {'guest_ip': LOCALHOST,
                                            'guest_port': '65002',
                                            'host_ip': LOCALHOST,
                                            'host_port': '65002'}],
                             'nginx':[{'proxied_ip': LOCALHOST,
                                       'proxied_port': '65000',
                                       'host_address': 'local.gcapi.com',
                                       'host_port': '82'},
                                      {'proxied_ip': LOCALHOST,
                                       'proxied_port': '65001',
                                       'host_address': 'local.gc.com',
                                       'host_port': '80'},
                                      {'proxied_ip': LOCALHOST,
                                       'proxied_port': '65002',
                                       'host_address': 'local.gc.com',
                                       'host_port': '81'}],
                             'hosts_file':[{'forwarded_ip': LOCALHOST,
                                            'host_address': 'local.gcapi.com'},
                                           {'forwarded_ip': LOCALHOST,
                                            'host_address': 'local.gc.com'}]}
        self.assertEqual(get_port_spec_document(expanded_spec), correct_port_spec)
