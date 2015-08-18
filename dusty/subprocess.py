"""Module for running subprocesses.  Providies features such as
demotion, to execute the process as another user, log streaming
to the client"""

from __future__ import absolute_import

import os
import pwd
import subprocess
import logging
from copy import copy

from .config import get_config_value
from .log import log_to_client
from . import constants

def _demote_to_user(user_name):
    def _demote():
        pw_record = pwd.getpwnam(user_name)
        _set_demoted_home_dir(user_name)
        os.setgid(pw_record.pw_gid)
        os.setuid(pw_record.pw_uid)
    return _demote

def _set_demoted_home_dir(user_name):
    home_dir = os.path.expanduser('~{}'.format(user_name))
    os.environ['HOME'] = home_dir

def run_subprocess(fn, shell_args, demote=True, env=None, **kwargs):
    if env:
        passed_env = copy(os.environ)
        passed_env.update(env)
    else:
        passed_env = None
    if demote:
        kwargs['preexec_fn'] = _demote_to_user(get_config_value(constants.CONFIG_MAC_USERNAME_KEY))
    output = fn(shell_args, env=passed_env, **kwargs)
    return output

def call_demoted(shell_args, env=None, redirect_stderr=False):
    kwargs = {} if not redirect_stderr else {'stderr': subprocess.STDOUT}
    return run_subprocess(subprocess.call, shell_args, demote=True, env=env, **kwargs)

def check_call(shell_args, demote=True, env=None, redirect_stderr=False):
    kwargs = {} if not redirect_stderr else {'stderr': subprocess.STDOUT}
    return run_subprocess(subprocess.check_call, shell_args, demote=demote, env=env, **kwargs)

def check_call_demoted(shell_args, env=None, redirect_stderr=False):
    return check_call(shell_args, demote=True, env=env, redirect_stderr=redirect_stderr)

def check_output(shell_args, demote=True, env=None, redirect_stderr=False):
    kwargs = {} if not redirect_stderr else {'stderr': subprocess.STDOUT}
    return run_subprocess(subprocess.check_output, shell_args, demote=demote, env=env, **kwargs)

def check_output_demoted(shell_args, env=None, redirect_stderr=False):
    return check_output(shell_args, env=env, redirect_stderr=redirect_stderr, demote=True)

def check_and_log_output_and_error_demoted(shell_args, env=None, strip_newlines=False, quiet_on_success=False):
    return check_and_log_output_and_error(shell_args, demote=True, env=env, strip_newlines=strip_newlines, quiet_on_success=quiet_on_success)

def check_and_log_output_and_error(shell_args, demote=True, env=None, strip_newlines=False, quiet_on_success=False):
    total_output = ""
    process = run_subprocess(subprocess.Popen, shell_args, demote=demote, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for output in iter(process.stdout.readline, ''):
        if not strip_newlines or output.strip('\n') != '':
            total_output += output
            if not quiet_on_success:
                log_to_client(output.strip())
    return_code = process.wait()
    if return_code != 0:
        if quiet_on_success:
            log_to_client(total_output)
        raise subprocess.CalledProcessError(return_code, ' '.join(shell_args))
    return total_output
