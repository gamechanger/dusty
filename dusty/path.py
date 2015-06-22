import os
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

