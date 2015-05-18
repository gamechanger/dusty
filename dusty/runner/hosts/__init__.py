import logging
import re

from ... import constants
from ...notifier import notify

DUSTY_CONFIG_REGEX = re.compile('\# BEGIN section for Dusty.*\# END section for Dusty\n', flags=re.DOTALL | re.MULTILINE)

def _read_hosts(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def _write_hosts(filepath, contents):
    with open(filepath, 'w') as f:
        f.write(contents)

def _remove_current_dusty_config(hosts):
    return DUSTY_CONFIG_REGEX.sub("", hosts)

def _add_dusty_config(hosts, hosts_spec):
    to_add = '# BEGIN section for Dusty\n'
    for spec in hosts_spec:
        address, ip = spec['host_address'], spec['forwarded_ip']
        to_add += '{} {}\n'.format(ip, address)
    to_add += '# END section for Dusty\n'
    return hosts + to_add

def update_hosts_from_port_spec(port_spec):
    hosts_spec = port_spec['hosts_file']
    logging.info('Updating hosts file to match spec: {}'.format(hosts_spec))
    current_hosts = _read_hosts(constants.HOSTS_PATH)
    cleared_hosts = _remove_current_dusty_config(current_hosts)
    updated_hosts = _add_dusty_config(cleared_hosts, hosts_spec)
    _write_hosts(constants.HOSTS_PATH, updated_hosts)
