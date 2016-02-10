class ReusedHostFullAddress(Exception):
    pass

class ReusedStreamHostPort(Exception):
    pass

def _docker_compose_port_spec(host_forwarding_spec, host_port):
    return {'in_container_port': str(host_forwarding_spec['container_port']),
            'mapped_host_port': str(host_port)}

def _nginx_port_spec(host_forwarding_spec, port, docker_vm_ip):
    return {'proxied_port': str(port),
            'host_address': host_forwarding_spec['host_name'],
            'host_port': str(host_forwarding_spec['host_port']),
            'type': host_forwarding_spec['type']}

def _hosts_file_port_spec(vm_ip, host_forwarding_spec):
    return {'forwarded_ip': vm_ip,
            'host_address': host_forwarding_spec['host_name']}

def _add_full_addresses(host_forwarding_spec, host_full_addresses):
    host_full_address = '{}:{}'.format(host_forwarding_spec['host_name'], host_forwarding_spec['host_port'])
    if host_full_address in host_full_addresses:
        raise ReusedHostFullAddress("{} has already been specified and used".format(host_full_address))
    host_full_addresses.add(host_full_address)

def _add_stream_host_port(host_forwarding_spec, stream_host_ports):
    stream_host_port = host_forwarding_spec['host_port']
    if stream_host_port in stream_host_ports:
        raise ReusedStreamHostPort("Host port {} is already being used by another stream-type host forwarding".format(stream_host_port))
    stream_host_ports.add(stream_host_port)

def _add_host_names(host_forwarding_spec, vm_ip, port_mappings, host_names):
    host_name = host_forwarding_spec['host_name']
    if host_name not in host_names:
        port_mappings['hosts_file'].append(_hosts_file_port_spec(vm_ip, host_forwarding_spec))
        host_names.add(host_name)

def get_port_spec_document(expanded_active_specs, docker_vm_ip):
    """ Given a dictionary containing the expanded dusty DAG specs this function will
    return a dictionary containing the port mappings needed by downstream methods.  Currently
    this includes docker_compose, virtualbox, nginx and hosts_file."""
    forwarding_port = 65000
    port_spec = {'docker_compose':{}, 'nginx':[], 'hosts_file':[]}
    host_full_addresses, host_names, stream_host_ports = set(), set(), set()
    # No matter the order of apps in expanded_active_specs, we want to produce a consistent
    # port_spec with respect to the apps and the ports they are outputted on
    for app_name in sorted(expanded_active_specs['apps'].keys()):
        app_spec = expanded_active_specs['apps'][app_name]
        if 'host_forwarding' not in app_spec:
            continue
        port_spec['docker_compose'][app_name] = []
        for host_forwarding_spec in app_spec['host_forwarding']:
            # These functions are just used for validating the set of specs all works together
            _add_full_addresses(host_forwarding_spec, host_full_addresses)
            if host_forwarding_spec['type'] == 'stream':
                _add_stream_host_port(host_forwarding_spec, stream_host_ports)

            port_spec['docker_compose'][app_name].append(_docker_compose_port_spec(host_forwarding_spec, forwarding_port))
            port_spec['nginx'].append(_nginx_port_spec(host_forwarding_spec, forwarding_port, docker_vm_ip))

            _add_host_names(host_forwarding_spec, docker_vm_ip, port_spec, host_names)
            forwarding_port += 1
    return port_spec
