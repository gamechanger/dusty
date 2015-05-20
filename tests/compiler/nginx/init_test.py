from unittest import TestCase
from dusty.compiler.nginx import (get_nginx_configuration_spec, _nginx_listen_string, _nginx_location_spec,
                                  _nginx_proxy_string, _nginx_server_spec)

def cleanse(string):
    return string.replace("\n", "").replace("\t", "").replace(" ", "")

class TestPortSpecCompiler(TestCase):
    def setUp(self):
        self.port_spec_dict_1 = {'nginx': [{'proxied_ip': '127.0.0.1',
                                            'proxied_port':'80',
                                            'host_address': 'local.gc.com',
                                            'host_port': '80'}]}
        self.port_spec_dict_2 = {'nginx': [{'proxied_ip': '127.0.0.0',
                                            'proxied_port':'8000',
                                            'host_address': 'local.gcapi.com',
                                            'host_port': '8001'}]}

    def test_get_nginx_configuration_spec_1(self):
        expected_output = cleanse("""http {
            server {
                listen local.gc.com:80;
                location / {
                    proxy_pass 127.0.0.1:80;
                }
            }
        }
        """)
        output = cleanse(get_nginx_configuration_spec(self.port_spec_dict_1))
        self.assertEqual(output, expected_output)

    def test_get_nginx_configuration_spec_2(self):
        expected_output = cleanse("""http {
            server {
                listen local.gcapi.com:8001;
                location / {
                    proxy_pass 127.0.0.0:8000;
                }
            }
        }
        """)
        output = cleanse(get_nginx_configuration_spec(self.port_spec_dict_2))
        self.assertEqual(output, expected_output)

    def test_get_nginx_configuration_spec_3(self):
        port_spec = {'nginx': [{'proxied_ip': '127.0.0.0',
                                'proxied_port':'8000',
                                'host_address': 'local.gcapi.com',
                                'host_port': '8001'},
                               {'proxied_ip': '127.0.0.1',
                                'proxied_port':'80',
                                'host_address': 'local.gc.com',
                                'host_port': '80'}]}

        expected_output = cleanse("""http {
            server {
                listen local.gcapi.com:8001;
                location / {
                    proxy_pass 127.0.0.0:8000;
                }
            }
            server {
                listen local.gc.com:80;
                location / {
                    proxy_pass 127.0.0.1:80;
                }
            }
        }
        """)
        output = cleanse(get_nginx_configuration_spec(port_spec))
        self.assertEqual(output, expected_output)


    def test_nginx_listen_string_1(self):
        self.assertEqual("listen local.gc.com:80;", _nginx_listen_string(self.port_spec_dict_1['nginx'][0]))

    def test_nginx_listen_string_2(self):
        self.assertEqual("listen local.gcapi.com:8001;", _nginx_listen_string(self.port_spec_dict_2['nginx'][0]))

    def test_nginx_proxy_string_1(self):
        self.assertEqual("proxy_pass 127.0.0.1:80;", _nginx_proxy_string(self.port_spec_dict_1['nginx'][0]))

    def test_nginx_proxy_string_2(self):
        self.assertEqual("proxy_pass 127.0.0.0:8000;", _nginx_proxy_string(self.port_spec_dict_2['nginx'][0]))
