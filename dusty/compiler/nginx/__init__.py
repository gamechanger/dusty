from ...constants import NGINX_MAX_FILE_SIZE, NGINX_502_PAGE_NAME

def _nginx_proxy_string(port_spec, bridge_ip):
    return "proxy_pass {}{}:{};".format('http://' if port_spec['type'] == 'http' else '',
                                        bridge_ip,
                                        port_spec['proxied_port'])

def _nginx_location_spec(port_spec, bridge_ip):
    """This will output the nginx location config string for specific port spec """
    location_string_spec = "\t \t location / { \n"
    for location_setting in ['proxy_http_version 1.1;',
                             'proxy_set_header Upgrade $http_upgrade;',
                             'proxy_set_header Connection "upgrade";',
                             'proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
                             'proxy_set_header Host $host;',
                             _nginx_proxy_string(port_spec, bridge_ip)]:
        location_string_spec += "\t \t \t {} \n".format(location_setting)
    location_string_spec += "\t \t } \n"
    return location_string_spec

def _nginx_listen_string(port_spec):
    return "listen {};".format(port_spec['host_port'])

def _nginx_server_name_string(port_spec):
    return "server_name {};".format(port_spec['host_address'])

def _nginx_max_file_size_string():
    return "client_max_body_size {};".format(NGINX_MAX_FILE_SIZE)

def _custom_502_page():
    return """
\t \t error_page 502 /{0};
\t \t location = /{0} {{
\t \t \t root /etc/nginx/conf.d/html;
\t \t \t internal;
\t \t }}\n""".format(NGINX_502_PAGE_NAME)

def _nginx_http_spec(port_spec, bridge_ip):
    """This will output the nginx HTTP config string for specific port spec """
    server_string_spec = "\t server {\n"
    server_string_spec += "\t \t {}\n".format(_nginx_max_file_size_string())
    server_string_spec += "\t \t {}\n".format(_nginx_listen_string(port_spec))
    server_string_spec += "\t \t {}\n".format(_nginx_server_name_string(port_spec))
    server_string_spec += _nginx_location_spec(port_spec, bridge_ip)
    server_string_spec += _custom_502_page()
    server_string_spec += "\t }\n"
    return server_string_spec

def _nginx_stream_spec(port_spec, bridge_ip):
    """This will output the nginx stream config string for specific port spec """
    server_string_spec = "\t server {\n"
    server_string_spec += "\t \t {}\n".format(_nginx_listen_string(port_spec))
    server_string_spec += "\t \t {}\n".format(_nginx_proxy_string(port_spec, bridge_ip))
    server_string_spec += "\t }\n"
    return server_string_spec

def get_nginx_configuration_spec(port_spec_dict, docker_bridge_ip):
    """This function will take in a port spec as specified by the port_spec compiler and
    will output an nginx web proxy config string. This string can then be written to a file
    and used running nginx """
    nginx_http_config, nginx_stream_config = "", ""
    for port_spec in port_spec_dict['nginx']:
        if port_spec['type'] == 'http':
            nginx_http_config += _nginx_http_spec(port_spec, docker_bridge_ip)
        elif port_spec['type'] == 'stream':
            nginx_stream_config += _nginx_stream_spec(port_spec, docker_bridge_ip)
    return {'http': nginx_http_config, 'stream': nginx_stream_config}
