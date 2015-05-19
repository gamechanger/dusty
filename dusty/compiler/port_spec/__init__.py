from dusty.constants import LOCALHOST

class ReusedHostFullAddress(Exception):
    pass

class ReusedContainerPort(Exception):
    pass

def _docker_compose_port_spec(host_forwarding_spec, host_port):
    return {'in_container_port': str(host_forwarding_spec['container_port']),
            'mapped_host_ip': LOCALHOST,
            'mapped_host_port': str(host_port)}

def _virtualbox_port_spec(port):
    return {'guest_ip': LOCALHOST,
            'guest_port': str(port),
            'host_ip': LOCALHOST,
            'host_port': str(port)}

def _nginx_port_spec(host_forwarding_spec, port):
    return {'proxied_ip': LOCALHOST,
            'proxied_port': str(port),
            'host_address': host_forwarding_spec['host_name'],
            'host_port': str(host_forwarding_spec['host_port'])}

def _hosts_file_port_spec(host_forwarding_spec):
    return {'forwarded_ip': LOCALHOST,
            'host_address': host_forwarding_spec['host_name']}


def host_forwarding_spec_document(host_forwarding_spec, forwarding_port, container_ports, host_full_addresses, host_names):
    """ Given a specific host_forwarding dictionary found in an dusty app spec, it will return the port_mappings for that
    host_forwarding. Currently this will include docker_compose, virtualbox, nginx and hosts_file"""
    port_spec = {'docker_compose': None, 'virtualbox': None, 'nginx': None, 'hosts_file': None}
    container_port = host_forwarding_spec['container_port']
    host_name = host_forwarding_spec['host_name']
    host_full_address = '{}:{}'.format(host_name, host_forwarding_spec['host_port'])

    if host_full_address in host_full_addresses:
        raise ReusedHostFullAddress("{} has already been specified and used".format(host_full_address))
    host_full_addresses.add(host_full_address)
    if container_port in container_ports:
        raise ReusedContainerPort("{} has already been specified and used".format(container_port))
    container_ports.add(container_port)

    port_spec['docker_compose'] = _docker_compose_port_spec(host_forwarding_spec, forwarding_port)
    port_spec['virtualbox'] = _virtualbox_port_spec(forwarding_port)
    port_spec['nginx'] = _nginx_port_spec(host_forwarding_spec, forwarding_port)
    if host_name not in host_names:
        port_spec['hosts_file']  = _hosts_file_port_spec(host_forwarding_spec)
        host_names.add(host_name)
    return port_spec


def port_spec_document(expanded_active_specs):
    """ Given a dictionary containing the expanded dusty DAG specs this function will
    return a dictionary containing the port mappings needed by downstream methods.  Currently
    this includes docker_compose, virtualbox, nginx and hosts_file."""
    forwarding_port = 65000
    port_spec = {'docker_compose':{}, 'virtualbox':[], 'nginx':[], 'hosts_file':[]}
    host_full_addresses = set()
    host_names = set()
    # No matter the order of apps in expanded_active_specs, we want to produce a consistent
    # port_spec with respect to the apps and the ports they are outputted on
    for app_name in sorted(expanded_active_specs['apps'].keys()):
        app_spec = expanded_active_specs['apps'][app_name]
        if 'host_forwarding' not in app_spec:
            continue
        container_ports = set()
        for host_forwarding_spec in app_spec['host_forwarding']:
            host_forwarding_port_spec = host_forwarding_spec_document(host_forwarding_spec, forwarding_port, container_ports, host_full_addresses, host_names)
            port_spec['docker_compose'][app_name] = host_forwarding_port_spec['docker_compose']
            port_spec['virtualbox'].append(host_forwarding_port_spec['virtualbox'])
            port_spec['nginx'].append(host_forwarding_port_spec['nginx'])
            if host_forwarding_port_spec['hosts_file'] is not None:
                port_spec['hosts_file'].append(host_forwarding_port_spec['hosts_file'])
            forwarding_port += 1
    return port_spec


