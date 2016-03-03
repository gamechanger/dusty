import json
import os
import shutil
from subprocess import check_output, check_call, CalledProcessError
import tempfile
import urllib

import psutil

from .. import constants
from ..daemon import close_client_connection, clean_up_socket, shut_down_http_server
from ..log import log_to_client
from ..payload import daemon_command
from ..subprocess import check_and_log_output_and_error


def _get_latest_version():
    """Gets latest Dusty binary version using the GitHub api"""
    url = 'https://api.github.com/repos/{}/releases/latest'.format(constants.DUSTY_GITHUB_PATH)
    conn = urllib.urlopen(url)
    if conn.getcode() >= 300:
        raise RuntimeError('GitHub api returned code {}; can\'t determine latest version.  Aborting'.format(conn.getcode()))
    json_data = conn.read()
    return json.loads(json_data)['tag_name']

def _get_binary_url(version):
    return 'https://github.com/{}/releases/download/{}/{}'.format(constants.DUSTY_GITHUB_PATH, version, constants.DUSTY_BINARY_NAME)

def _get_binary_location():
    return psutil.Process().exe()

def _download_binary(version):
    binary_url = _get_binary_url(version)
    conn = urllib.urlopen(binary_url)
    if conn.getcode() >= 300:
        raise RuntimeError('Unable to retrieve Dusty binary version {} from GitHub; this version may not exist'.format(version))
    binary_data = conn.read()
    tmp_path = tempfile.mktemp()
    with open(tmp_path, 'w') as f:
        f.write(binary_data)
    os.chmod(tmp_path, 0755)
    return tmp_path

def _test_dusty_binary(binary_path, version):
    try:
        output = check_output([binary_path, '-v']).rstrip()
    except CalledProcessError:
        raise RuntimeError('Downloaded binary is not operating correctly; aborting upgrade')
    test_version = output.split()[-1]
    if 'RC' in version:
        log_to_client('Release candidate requested, skipping version check')
        return
    if test_version != version:
        raise RuntimeError('Version of downloaded binary {} does not match expected {}'.format(test_version, version))
    check_and_log_output_and_error([binary_path, '-d', '--preflight-only'], demote=False, quiet_on_success=True)

def _move_temp_binary_to_path(tmp_binary_path):
    """Moves the temporary binary to the location of the binary that's currently being run.
    Preserves owner, group, and permissions of original binary"""
    # pylint: disable=E1101
    binary_path = _get_binary_location()
    if not binary_path.endswith(constants.DUSTY_BINARY_NAME):
        raise RuntimeError('Refusing to overwrite binary {}'.format(binary_path))
    st = os.stat(binary_path)
    permissions = st.st_mode
    owner = st.st_uid
    group = st.st_gid
    shutil.move(tmp_binary_path, binary_path)
    os.chown(binary_path, owner, group)
    os.chmod(binary_path, permissions)
    return binary_path

@daemon_command
def upgrade_dusty_binary(version=None):
    if not constants.BINARY:
        log_to_client('It looks like you\'re running Dusty from source. Upgrade is only available when you use the installed binary')
        return
    if version is None:
        version = _get_latest_version()
    if not constants.PRERELEASE and version == constants.VERSION:
        log_to_client('You\'re already running the latest Dusty version ({})'.format(version))
        return
    else:
        log_to_client('Downloading Dusty version {}'.format(version))
    tmp_binary_path = _download_binary(version)
    _test_dusty_binary(tmp_binary_path, version)
    final_binary_path = _move_temp_binary_to_path(tmp_binary_path)
    log_to_client('Finished upgrade to version {} of Dusty!  The daemon will now restart'.format(version))
    log_to_client('You may need to run `dusty up` to fully complete the upgrade')
    shut_down_http_server()
    close_client_connection()
    clean_up_socket()
    os.execvp(final_binary_path, [final_binary_path, '-d'])
