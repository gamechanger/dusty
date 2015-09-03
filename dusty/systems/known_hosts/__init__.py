import os
import logging

from ...subprocess import check_output

def _get_known_hosts_path():
    ssh_dir = os.path.expanduser('~root/.ssh')
    if not os.path.isdir(ssh_dir):
        os.makedirs(ssh_dir)
    return os.path.join(ssh_dir, 'known_hosts')

def ensure_known_hosts(hosts):
    known_hosts_path = _get_known_hosts_path()
    modified = False
    with open(known_hosts_path, 'r+') as f:
        contents = f.read()
        if not contents.endswith('\n'):
            contents += '\n'
        for host in hosts:
            if host not in contents:
                logging.info('Adding {} ssh key to roots ssh known_hosts file'.format(host))
                command = ['sh', '-c', 'ssh-keyscan -t rsa {}'.format(host)]
                result = check_output(command, demote=False)
                contents += result
                modified = True
        if modified:
            f.seek(0)
            f.write(contents)
