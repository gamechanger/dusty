from ....testcases import DustyTestCase
from dusty.compiler.nginx import (get_nginx_configuration_spec, _nginx_listen_string, _nginx_location_spec,
                                  _nginx_proxy_string, _nginx_server_name_string)

def cleanse(string):
    return string.replace("\n", "").replace("\t", "").replace(" ", "")

class TestPortSpecCompiler(DustyTestCase):
    def setUp(self):
        super(TestPortSpecCompiler, self).setUp()
        self.port_spec_dict_1 = {'nginx': [{'proxied_port':'80',
                                            'host_address': 'local.gc.com',
                                            'host_port': '80',
                                            'type': 'http'}]}
        self.port_spec_dict_2 = {'nginx': [{'proxied_port':'8000',
                                            'host_address': 'local.gcapi.com',
                                            'host_port': '8001',
                                            'type': 'http'}]}
        self.port_spec_dict_3 = {'nginx': [{'proxied_port': '8000',
                                            'host_address': 'local.ssh.com',
                                            'host_port': '222',
                                            'type': 'stream'}]}

    def test_get_nginx_configuration_spec_1(self):
        expected_output = cleanse("""
            server {
                client_max_body_size 500M;
                listen 80;
                server_name local.gc.com;
                location / {
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "upgrade";
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header Host $host;
                    proxy_pass http://172.17.42.1:80;
                }
            }
        """)
        output = cleanse(get_nginx_configuration_spec(self.port_spec_dict_1)['http'])
        self.assertEqual(output, expected_output)

    def test_get_nginx_configuration_spec_2(self):
        expected_output = cleanse("""
            server {
                client_max_body_size 500M;
                listen 8001;
                server_name local.gcapi.com;
                location / {
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "upgrade";
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header Host $host;
                    proxy_pass http://172.17.42.1:8000;
                }
            }
        """)
        output = cleanse(get_nginx_configuration_spec(self.port_spec_dict_2)['http'])
        self.assertEqual(output, expected_output)

    def test_get_nginx_configuration_spec_3(self):
        port_spec = {'nginx': [{'proxied_port':'8000',
                                'host_address': 'local.gcapi.com',
                                'host_port': '8001',
                                'type': 'http'},
                               {'proxied_port':'80',
                                'host_address': 'local.gc.com',
                                'host_port': '80',
                                'type': 'http'}]}

        expected_output = cleanse("""
            server {
                client_max_body_size 500M;
                listen 8001;
                server_name local.gcapi.com;
                location / {
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "upgrade";
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header Host $host;
                    proxy_pass http://172.17.42.1:8000;
                }
            }
            server {
                client_max_body_size 500M;
                listen 80;
                server_name local.gc.com;
                location / {
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "upgrade";
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header Host $host;
                    proxy_pass http://172.17.42.1:80;
                }
            }
        """)
        output = cleanse(get_nginx_configuration_spec(port_spec)['http'])
        self.assertEqual(output, expected_output)

    def test_get_nginx_configuration_spec_stream(self):
        expected_output = cleanse("""
            server {
                listen 222;
                proxy_pass 172.17.42.1:8000;
            }
        """)
        output = cleanse(get_nginx_configuration_spec(self.port_spec_dict_3)['stream'])
        self.assertEqual(output, expected_output)

    def test_nginx_listen_string_1(self):
        self.assertEqual("listen 80;", _nginx_listen_string(self.port_spec_dict_1['nginx'][0]))

    def test_nginx_listen_string_2(self):
        self.assertEqual("listen 8001;", _nginx_listen_string(self.port_spec_dict_2['nginx'][0]))

    def test_nginx_server_name_string_1(self):
        self.assertEqual("server_name local.gc.com;", _nginx_server_name_string(self.port_spec_dict_1['nginx'][0]))

    def test_nginx_server_name_string_2(self):
        self.assertEqual("server_name local.gcapi.com;", _nginx_server_name_string(self.port_spec_dict_2['nginx'][0]))

    def test_nginx_proxy_string_1(self):
        self.assertEqual("proxy_pass http://172.17.42.1:80;", _nginx_proxy_string(self.port_spec_dict_1['nginx'][0]))

    def test_nginx_proxy_string_2(self):
        self.assertEqual("proxy_pass http://172.17.42.1:8000;", _nginx_proxy_string(self.port_spec_dict_2['nginx'][0]))

    def test_nginx_proxy_string_3(self):
        self.assertEqual("proxy_pass 172.17.42.1:8000;", _nginx_proxy_string(self.port_spec_dict_3['nginx'][0]))
