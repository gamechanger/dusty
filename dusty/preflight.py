"""This module contains checks for system dependencies that are run
when dustyd first starts up. Any failed checks should throw an exception
which bubbles up to the daemon and causes it to crash."""

import os
import logging
import subprocess
import warnings

from .log import ROOT_LOG_DIR, root_log_dir_is_writable, ensure_log_subdirs_exist

VERSIONS = {
    'nginx': '1.8.0',
    'virtualbox': '4.3.26',
    'boot2docker': '1.6.0',
    'docker': '1.6.0'
}

class PreflightException(Exception):
    pass

def _assert_executable_exists(executable_name):
    logging.info('Checking for existence of {}'.format(executable_name))
    try:
        subprocess.check_output('which {}'.format(executable_name), shell=True)
    except subprocess.CalledProcessError, OSError:
        raise PreflightException('Executable not found: {}'.format(executable_name))

def _maybe_version_warning(executable, installed_version):
    if installed_version != VERSIONS[executable]:
        warnings.warn('Your {} version ({}) deviates from the supported version ({}).'.format(executable,
                                                                                              installed_version,
                                                                                              VERSIONS[executable]))

def check_nginx():
    _assert_executable_exists('nginx')
    installed_version = subprocess.check_output(['nginx', '-v'], stderr=subprocess.STDOUT).strip().split('/')[-1]
    _maybe_version_warning('nginx', installed_version)

def check_virtualbox():
    _assert_executable_exists('VBoxManage')
    installed_version = subprocess.check_output(['VBoxManage', '-v']).split('r')[0]
    _maybe_version_warning('virtualbox', installed_version)

def check_boot2docker():
    _assert_executable_exists('boot2docker')
    installed_version = subprocess.check_output(['boot2docker', 'version']).splitlines()[0].split(':')[1].split('v')[-1]
    _maybe_version_warning('boot2docker', installed_version)

def check_docker():
    _assert_executable_exists('docker')
    installed_version = subprocess.check_output(['docker', '-v']).split(',')[0].split(' ')[-1]
    _maybe_version_warning('docker', installed_version)

def check_root_log_dir():
    os.access

def preflight_check():
    logging.info('Starting preflight check')
    check_nginx()
    check_virtualbox()
    check_boot2docker()
    check_docker()
    if not root_log_dir_is_writable():
        raise PreflightException('Root log directory {} is not writable'.format(ROOT_LOG_DIR))
    ensure_log_subdirs_exist()
    logging.info('Completed preflight check successfully')
