from unittest import TestCase
from dusty.compiler.nginx import (nginx_configuration_spec, _nginx_listen_string, _nginx_location_spec,
                                  _nginx_proxy_string, _nginx_server_spec)

def clense(string):
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

    def test_nginx_configuration_spec_1(self):
        expected_output = clense("""http {
            server {
                listen local.gc.com:80;
                location / {
                    proxy_pass 127.0.0.1:80;
                }
            }
        }
        """)
        output = clense(nginx_configuration_spec(self.port_spec_dict_1))
        print output
        self.assertEqual(output, expected_output)

    def test_nginx_configuration_spec_2(self):
        expected_output = clense("""http {
            server {
                listen local.gcapi.com:80001;
                location / {
                    proxy_pass 127.0.0.0:8000;
                }
            }
        }
        """)
        output = clense(nginx_configuration_spec(self.port_spec_dict_2))
        print output
        self.assertEqual(output, expected_output)
