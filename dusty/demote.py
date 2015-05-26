import os
import pwd
import subprocess
import logging
from threading import Thread
from copy import copy

from .config import get_config_value
from .log import log_to_client, log_to_client_only

def _demote_to_user(user_name):
    def _demote():
        pw_record = pwd.getpwnam(user_name)
        os.setgid(pw_record.pw_gid)
        os.setuid(pw_record.pw_uid)
    return _demote

def _check_demoted(fn, shell_args, env=None, **kwargs):
    if env:
        passed_env = copy(os.environ)
        passed_env.update(env)
    else:
        passed_env = None
    output = fn(shell_args, preexec_fn=_demote_to_user(get_config_value('mac_username')), env=passed_env, **kwargs)
    return output

def check_call_demoted(shell_args, env=None):
    return _check_demoted(subprocess.check_call, shell_args, env)

def check_output_demoted(shell_args, env=None):
    return _check_demoted(subprocess.check_output, shell_args, env)

def check_and_log_output_and_error_demoted(shell_args, env=None):
    total_output = ""
    process = _check_demoted(subprocess.Popen, shell_args, env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for output in iter(process.stdout.readline, ''):
        total_output += output
        log_to_client(output.strip())
    return total_output

def thread_output_client_only(shell_args, env=None):
    process = _check_demoted(subprocess.Popen, shell_args, env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for output in iter(process.stdout.readline, ''):
        log_to_client_only(output.strip())
