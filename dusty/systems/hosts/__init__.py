import logging

from ... import constants
from .. import config_file


def _dusty_hosts_config(hosts_specs):
    """Return a string of all host rules required to match
    the given spec. This string is wrapped in the Dusty hosts
    header and footer so it can be easily removed later."""
    rules =  ''.join(['{} {}\n'.format(spec['forwarded_ip'], spec['host_address']) for spec in hosts_specs])
    return config_file.create_config_section(rules)

def update_hosts_file_from_port_spec(port_spec):
    """Given a port spec, update the hosts file specified at
    constants.HOST_PATH to contain the port mappings specified
    in the spec. Any existing Dusty configurations are replaced."""
    logging.info('Updating hosts file to match port spec')
    hosts_specs = port_spec['hosts_file']
    current_hosts = config_file.read(constants.HOSTS_PATH)
    cleared_hosts = config_file.remove_current_dusty_config(current_hosts)
    updated_hosts = cleared_hosts + _dusty_hosts_config(hosts_specs)
    config_file.write(constants.HOSTS_PATH, updated_hosts)
