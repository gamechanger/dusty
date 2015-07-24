from ...constants import NGINX_MAX_FILE_SIZE, VM_IP_FROM_DOCKER

def _nginx_proxy_string(port_spec):
    return "proxy_pass http://{}:{};".format(VM_IP_FROM_DOCKER, port_spec['proxied_port'])

def _nginx_location_spec(port_spec):
    """This will output the nginx location config string for speicfic port spec """
    location_string_spec = "\t \t location / { \n"
    for location_setting in ['proxy_http_version 1.1;',
                             'proxy_set_header Upgrade $http_upgrade;',
                             'proxy_set_header Connection "upgrade";',
                             'proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
                             'proxy_set_header Host $host;',
                             _nginx_proxy_string(port_spec)]:
        location_string_spec += "\t \t \t {} \n".format(location_setting)
    location_string_spec += "\t \t } \n"
    return location_string_spec

def _nginx_listen_string(port_spec):
    return "listen {};".format(port_spec['host_port'])

def _nginx_server_name_string(port_spec):
    return "server_name {};".format(port_spec['host_address'])

def _nginx_max_file_size_string():
    return "client_max_body_size {};".format(NGINX_MAX_FILE_SIZE)

def _nginx_server_spec(port_spec):
    """This will output the nginx server config string for speicfic port spec """
    server_string_spec = "\t server {\n"
    server_string_spec += "\t \t {}\n".format(_nginx_max_file_size_string())
    server_string_spec += "\t \t {}\n".format(_nginx_listen_string(port_spec))
    server_string_spec += "\t \t {}\n".format(_nginx_server_name_string(port_spec))
    server_string_spec += _nginx_location_spec(port_spec)
    server_string_spec += "\t }\n"
    return server_string_spec

def get_nginx_configuration_spec(port_spec_dict):
    """This function will take in a port spec as specified by the port_spec compiler and
    will output an nginx web proxy config string. This string can then be written to a file
    and used running nginx """
    nginx_string_spec = ""
    for port_spec in port_spec_dict['nginx']:
        nginx_string_spec += _nginx_server_spec(port_spec)
    return nginx_string_spec
