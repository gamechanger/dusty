import urllib
import os
from subprocess import check_output, check_call

from .. import constants
from ..daemon import close_connection
from ..log import log_to_client
from ..payload import daemon_command


def _get_latest_version():
    """Gets latest Dusty binary version using the GitHub api"""
    pass

def _get_binary_url(version):
    return 'https://github.com/gamechanger/dusty/releases/download/{}/dusty'.format(version)

def _get_binary_location():
    return check_output(['which', 'dusty']).rstrip()

def _download_and_replace_binary(version):
    binary_url = _get_binary_url(version)
    binary_location = _get_binary_location()
    conn = urllib.urlopen(binary_url)
    if conn.getcode() >= 300:
        raise RuntimeError('Unable to retrieve Dusty binary version {} from {}'.format(version, binary_url))
    binary_data = conn.read()
    with open(binary_location, 'w') as f:
        f.write(binary_data)
    log_to_client('Downloaded and replaced Dusty binary at {}'.format(binary_location))

@daemon_command
def upgrade_dusty_binary(version=None):
    if not constants.BINARY:
        log_to_client("The dusty upgrade command only works when dusty is run with its binaries")
        return
    if version is None:
        version = _get_latest_version()
    _download_and_replace_binary(version)
    close_connection()
    os.execvp('dusty', ['dusty', '-d'])
