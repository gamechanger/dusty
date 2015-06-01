from ...utils import DustyTestCase
from dusty.compiler.nginx import (get_nginx_configuration_spec, _nginx_listen_string, _nginx_location_spec,
                                  _nginx_proxy_string, _nginx_server_spec, _nginx_server_name_string)

def cleanse(string):
    return string.replace("\n", "").replace("\t", "").replace(" ", "")

class TestPortSpecCompiler(DustyTestCase):
    def setUp(self):
        super(TestPortSpecCompiler, self).setUp()
        self.port_spec_dict_1 = {'nginx': [{'proxied_port':'80',
                                            'boot2docker_ip': '127.0.0.0',
                                            'host_address': 'local.gc.com',
                                            'host_port': '80'}]}
        self.port_spec_dict_2 = {'nginx': [{'proxied_port':'8000',
                                            'boot2docker_ip': '127.0.0.0',
                                            'host_address': 'local.gcapi.com',
                                            'host_port': '8001'}]}

    def test_get_nginx_configuration_spec_1(self):
        expected_output = cleanse("""http {
            server {
                client_max_body_size 500M;
                listen 80;
                server_name local.gc.com;
                location / {
                    proxy_pass http://127.0.0.0:80;
                }
            }
        }
        """)
        output = cleanse(get_nginx_configuration_spec(self.port_spec_dict_1))
        self.assertEqual(output, expected_output)

    def test_get_nginx_configuration_spec_2(self):
        expected_output = cleanse("""http {
            server {
                client_max_body_size 500M;
                listen 8001;
                server_name local.gcapi.com;
                location / {
                    proxy_pass http://127.0.0.0:8000;
                }
            }
        }
        """)
        output = cleanse(get_nginx_configuration_spec(self.port_spec_dict_2))
        self.assertEqual(output, expected_output)

    def test_get_nginx_configuration_spec_3(self):
        port_spec = {'nginx': [{'proxied_port':'8000',
                                'boot2docker_ip': '127.0.0.0',
                                'host_address': 'local.gcapi.com',
                                'host_port': '8001'},
                               {'proxied_port':'80',
                                'host_address': 'local.gc.com',
                                'boot2docker_ip': '127.0.0.0',
                                'host_port': '80'}]}

        expected_output = cleanse("""http {
            server {
                client_max_body_size 500M;
                listen 8001;
                server_name local.gcapi.com;
                location / {
                    proxy_pass http://127.0.0.0:8000;
                }
            }
            server {
                client_max_body_size 500M;
                listen 80;
                server_name local.gc.com;
                location / {
                    proxy_pass http://127.0.0.0:80;
                }
            }
        }
        """)
        output = cleanse(get_nginx_configuration_spec(port_spec))
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
        self.assertEqual("proxy_pass http://127.0.0.0:80;", _nginx_proxy_string(self.port_spec_dict_1['nginx'][0]))

    def test_nginx_proxy_string_2(self):
        self.assertEqual("proxy_pass http://127.0.0.0:8000;", _nginx_proxy_string(self.port_spec_dict_2['nginx'][0]))
