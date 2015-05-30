import os
from . import constants
from .config import get_config_value

def local_repo_path(repo_name):
    """Given a repo_name (github.com/gamechanger/gclib), checks if that repo has an
    override, and returns the appropriate directory"""
    repo_overrides = get_config_value('repo_overrides')
    override_dir = repo_overrides.get(repo_name)
    return override_dir if override_dir else managed_repo_path(repo_name)

def vm_repo_path(repo_name):
    return os.path.join(constants.VM_REPOS_DIR, repo_name)

def managed_repo_path(repo_name):
    return os.path.join(constants.REPOS_DIR, repo_name)
