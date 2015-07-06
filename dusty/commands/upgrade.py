import json
import os
import shutil
from subprocess import check_output, check_call, CalledProcessError
import urllib

from .. import constants
from ..daemon import close_client_connection
from ..log import log_to_client
from ..payload import daemon_command


def _get_latest_version():
    """Gets latest Dusty binary version using the GitHub api"""
    url = 'https://api.github.com/repos/gamechanger/dusty/releases/latest'
    conn = urllib.urlopen(url)
    json_data = conn.read()
    return json.loads(json_data)['tag_name']

def _get_binary_url(version):
    return 'https://github.com/gamechanger/dusty/releases/download/{}/dusty'.format(version)

def _get_binary_location():
    return check_output(['which', 'dusty']).rstrip()

def _download_binary(version):
    binary_url = _get_binary_url(version)
    conn = urllib.urlopen(binary_url)
    if conn.getcode() >= 300:
        raise RuntimeError('Unable to retrieve Dusty binary version {} from GitHub; this version may not exist'.format(version))
    binary_data = conn.read()
    with open(constants.TEMP_BIN_PATH, 'w') as f:
        f.write(binary_data)
    os.chmod(constants.TEMP_BIN_PATH, 0755)

def _test_dusty_binary(version):
    try:
        output = check_output([constants.TEMP_BIN_PATH, '-v']).rstrip()
    except CalledProcessError:
        raise RuntimeError('Downloaded binary is not operating correctly; aborting upgrade')
    test_version = output.split()[-1]
    if test_version != version:
        raise RuntimeError('Version of downloaded binary {} does not match expected {}'.format(test_version, version))

def _move_temp_binary_to_path():
    """Moves the temporary binary to the location of the binary with the user's PATH.
    Preserves owner, group, and permissions of original binary"""
    binary_path = _get_binary_location()
    st = os.stat(binary_path)
    permissions = st.st_mode
    owner = st.st_uid
    group = st.st_gid
    shutil.move(constants.TEMP_BIN_PATH, binary_path)
    os.chown(binary_path, owner, group)
    os.chmod(binary_path, permissions)

@daemon_command
def upgrade_dusty_binary(version=None):
    if not constants.BINARY:
        log_to_client("The dusty upgrade command only works when dusty is run with its binaries")
        return
    if version is None:
        version = _get_latest_version()
        log_to_client('Downloading latest Dusty version: {}'.format(version))
    _download_binary(version)
    _test_dusty_binary(version)
    _move_temp_binary_to_path()
    log_to_client('Finished upgrade to version {} of Dusty!  The daemon will now restart'.format(version))
    close_client_connection()
    os.execvp('dusty', ['dusty', '-d'])
