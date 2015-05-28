import subprocess

from .. import constants
from ..log import log_to_client
from ..demote import check_output_demoted

DIAGNOSTIC_COMMANDS = [
    ['nginx', '-v'],
    ['which', 'rsync'],
    ['VBoxManage', '-v'],
    ['boot2docker', 'version'],
    ['docker', '-v'],
    ['docker-compose', '--version'],
    ['cat', constants.HOSTS_PATH],
    ['cat', constants.CONFIG_PATH],
    ['VBoxManage', 'showvminfo', 'boot2docker-vm'],
    ['ssh-add', '-l']
]

def dump_diagnostics():
    for command in DIAGNOSTIC_COMMANDS:
        log_to_client('COMMAND: {}'.format(' '.join(command)))
        log_to_client('OUTPUT:')
        try:
            output = check_output_demoted(command, redirect_stderr=True)
        except subprocess.CalledProcessError as e:
            output = e.output
        log_to_client(output)
        log_to_client('')
