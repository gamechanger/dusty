"""This module contains checks for system dependencies that are run
when dustyd first starts up. Any failed checks should throw an exception
which bubbles up to the daemon and causes it to crash."""

import os
import logging
import subprocess
import warnings

from .config import write_default_config
from .constants import RUN_DIR, ROOT_LOG_DIR, LOG_SUBDIRS, SYSTEM_DEPENDENCY_VERSIONS, CONFIG_DIR, CONFIG_PATH

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

def _check_rsync():
    _assert_executable_exists('rsync')

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

def _ensure_run_dir_exists():
    if not os.path.exists(RUN_DIR):
        os.makedirs(RUN_DIR)

def _ensure_root_log_dir_exists():
    if not os.path.exists(ROOT_LOG_DIR):
        os.makedirs(ROOT_LOG_DIR)

def _ensure_config_dir_exists():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def _ensure_log_subdirs_exist():
    for subdir in LOG_SUBDIRS:
        subdir_path = os.path.join(ROOT_LOG_DIR, subdir)
        if not os.path.exists(subdir_path):
            logging.info('Creating logging subdir {}'.format(subdir_path))
            os.mkdir(subdir_path)

def preflight_check():
    logging.info('Starting preflight check')
    _check_nginx()
    _check_rsync()
    _check_virtualbox()
    _check_boot2docker()
    _check_docker()
    _ensure_run_dir_exists()
    _ensure_root_log_dir_exists()
    _ensure_config_dir_exists()
    _ensure_log_subdirs_exist()
    if not os.path.exists(CONFIG_PATH):
        logging.info('Creating default config file at {}'.format(CONFIG_PATH))
        write_default_config()
    logging.info('Completed preflight check successfully')
