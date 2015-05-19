def _nginx_proxy_string(port_spec):
    return "proxy_pass {}:{};".format(port_spec['proxied_ip'], port_spec['proxied_port'])

def _nginx_location_spec(port_spec):
    location_string_spec = "\t \t location / { \n"
    location_string_spec += "\t \t \t {} \n".format(_nginx_proxy_string(port_spec))
    location_string_spec += "\t \t } \n"
    return location_string_spec

def _nginx_listen_string(port_spec):
    return "listen {}:{};".format(port_spec['host_address'], port_spec['host_port'])

def _nginx_server_spec(port_spec):
    server_string_spec = "\t server {\n"
    server_string_spec += "\t \t {}\n".format(_nginx_listen_string(port_spec))
    server_string_spec += _nginx_location_spec(port_spec)
    server_string_spec += "\t }\n"
    return server_string_spec

def nginx_configuration_spec(port_spec_dict):
    nginx_string_spec = "http { \n"
    for port_spec in port_spec_dict['nginx']:
        nginx_string_spec += _nginx_server_spec(port_spec)
    nginx_string_spec += "}\n"
    return nginx_string_spec
