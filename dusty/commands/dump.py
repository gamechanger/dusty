import subprocess

from .. import constants
from ..log import log_to_client
from ..subprocess import check_output_demoted
from ..warnings import daemon_warnings

DIAGNOSTIC_SUBPROCESS_COMMANDS = [
    ['nginx', '-v'],
    ['which', 'rsync'],
    ['VBoxManage', '-v'],
    ['boot2docker', 'version'],
    ['boot2docker', 'ssh', 'df', '-h'],
    ['docker', '-v'],
    ['docker-compose', '--version'],
    ['cat', constants.HOSTS_PATH],
    ['cat', constants.CONFIG_PATH],
    ['VBoxManage', 'showvminfo', 'boot2docker-vm'],
    ['ssh-add', '-l']
]

DIAGNOSTIC_DUSTY_COMMANDS = [
    ('Dusty Version', lambda: constants.VERSION),
    ('Daemon Warnings', daemon_warnings.pretty)
]

def dump_diagnostics():
    for title, fn in DIAGNOSTIC_DUSTY_COMMANDS:
        log_to_client('COMMAND: {}'.format(title))
        log_to_client('OUTPUT:')
        log_to_client(fn())
        log_to_client('')

    for command in DIAGNOSTIC_SUBPROCESS_COMMANDS:
        log_to_client('COMMAND: {}'.format(' '.join(command)))
        log_to_client('OUTPUT:')
        try:
            output = check_output_demoted(command, redirect_stderr=True)
        except subprocess.CalledProcessError as e:
            output = e.output
        log_to_client(output)
        log_to_client('')
