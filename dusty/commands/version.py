from ..constants import VERSION
from ..log import log_to_client

def version():
    log_to_client('Dusty daemon version: {}'.format(VERSION))