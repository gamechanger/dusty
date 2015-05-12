"""This module contains checks for system dependencies that are run
when dustyd first starts up. Any failed checks should throw an exception
which bubbles up to the daemon and causes it to crash."""

import os
import logging
import subprocess
import warnings

from .config import write_default_user_config
from .constants import ROOT_LOG_DIR, LOG_SUBDIRS, SYSTEM_DEPENDENCY_VERSIONS, USER_CONFIG_PATH

class PreflightException(Exception):
    pass

def _assert_executable_exists(executable_name):
    logging.info('Checking for existence of {}'.format(executable_name))
    try:
        subprocess.check_output('which {}'.format(executable_name), shell=True)
    except subprocess.CalledProcessError, OSError:
        raise PreflightException('Executable not found: {}'.format(executable_name))

def _maybe_version_warning(executable, installed_version):
    if installed_version != SYSTEM_DEPENDENCY_VERSIONS[executable]:
        warnings.warn('Your {} version ({}) deviates from the supported version ({}).'.format(executable,
                                                                                              installed_version,
                                                                                              SYSTEM_DEPENDENCY_VERSIONS[executable]))

def _check_nginx():
    _assert_executable_exists('nginx')
    installed_version = subprocess.check_output(['nginx', '-v'], stderr=subprocess.STDOUT).strip().split('/')[-1]
    _maybe_version_warning('nginx', installed_version)

def _check_virtualbox():
    _assert_executable_exists('VBoxManage')
    installed_version = subprocess.check_output(['VBoxManage', '-v']).split('r')[0]
    _maybe_version_warning('virtualbox', installed_version)

def _check_boot2docker():
    _assert_executable_exists('boot2docker')
    installed_version = subprocess.check_output(['boot2docker', 'version']).splitlines()[0].split(':')[1].split('v')[-1]
    _maybe_version_warning('boot2docker', installed_version)

def _check_docker():
    _assert_executable_exists('docker')
    installed_version = subprocess.check_output(['docker', '-v']).split(',')[0].split(' ')[-1]
    _maybe_version_warning('docker', installed_version)

def _path_exists(path):
    return os.access(path, os.F_OK)

def _path_is_writable(path):
    return os.access(path, os.W_OK)

def _ensure_log_subdirs_exist():
    for subdir in LOG_SUBDIRS:
        subdir_path = os.path.join(ROOT_LOG_DIR, subdir)
        if not os.path.exists(subdir_path):
            logging.info('Creating logging subdir {}'.format(subdir_path))
            os.mkdir(subdir_path)

def preflight_check():
    logging.info('Starting preflight check')
    _check_nginx()
    _check_virtualbox()
    _check_boot2docker()
    _check_docker()
    if not _path_exists(ROOT_LOG_DIR):
        raise PreflightException('Root log directory {} does not exist'.format(ROOT_LOG_DIR))
    if not _path_is_writable(ROOT_LOG_DIR):
        raise PreflightException('Root log directory {} is not writable'.format(ROOT_LOG_DIR))
    _ensure_log_subdirs_exist()
    if not _path_exists(USER_CONFIG_PATH):
        logging.info('Creating default user config file at {}'.format(USER_CONFIG_PATH))
        write_default_user_config()
    logging.info('Completed preflight check successfully')
