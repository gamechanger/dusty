from __future__ import absolute_import

import os
import shutil
import subprocess
import time
import tempfile

from . import constants
from .config import get_config_value

def parent_dir(path):
    """Return the parent directory of a file or directory.
    This is commonly useful for creating parent directories
    prior to creating a file."""
    return os.path.split(path)[0]

def vm_cp_path(app_or_service_name):
    return os.path.join(constants.VM_CP_DIR, app_or_service_name)

def vm_command_files_path(app_or_service_name):
    return os.path.join(constants.VM_COMMAND_FILES_DIR, app_or_service_name)

def dir_modified_time(path):
    return time.ctime(os.path.getmtime(path))

def set_mac_user_ownership(path):
    command = "chown -R {} {}".format(get_config_value(constants.CONFIG_MAC_USERNAME_KEY), path).split()
    subprocess.check_call(command)

def case_insensitive_rename(src, dst):
    """A hack to allow us to rename paths in a case-insensitive filesystem like HFS."""
    temp_dir = tempfile.mkdtemp()
    shutil.rmtree(temp_dir)
    shutil.move(src, temp_dir)
    shutil.move(temp_dir, dst)
