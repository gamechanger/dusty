from ..constants import VERSION
from ..log import log_to_client
from ..payload import daemon_command

@daemon_command
def version():
    log_to_client('Dusty daemon version: {}'.format(VERSION))
