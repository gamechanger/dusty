def _nginx_proxy_string(port_spec):
    return "proxy_pass http://{}:{};".format("{0}", port_spec['proxied_port'])

def _nginx_location_spec(port_spec):
    """This will output the nginx location config string for speicfic port spec """
    location_string_spec = "\t \t location / {{ \n"
    location_string_spec += "\t \t \t {} \n".format(_nginx_proxy_string(port_spec))
    location_string_spec += "\t \t }} \n"
    return location_string_spec

def _nginx_listen_string(port_spec):
    return "listen {};".format(port_spec['host_port'])

def _nginx_server_name_string(port_spec):
    return "server_name {};".format(port_spec['host_address'])

def _nginx_server_spec(port_spec):
    """This will output the nginx server config string for speicfic port spec """
    server_string_spec = "\t server {{\n"
    server_string_spec += "\t \t {}\n".format(_nginx_listen_string(port_spec))
    server_string_spec += "\t \t {}\n".format(_nginx_server_name_string(port_spec))
    server_string_spec += _nginx_location_spec(port_spec)
    server_string_spec += "\t }}\n"
    return server_string_spec

def get_nginx_configuration_spec(port_spec_dict):
    """This function will take in a port spec as specified by the port_spec compiler and
    will output an nginx web proxy config string. This string can then be written to a file
    and used running nginx """
    nginx_string_spec = "http {{ \n"
    for port_spec in port_spec_dict['nginx']:
        nginx_string_spec += _nginx_server_spec(port_spec)
    nginx_string_spec += "}}\n"
    return nginx_string_spec
