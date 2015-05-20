import os
import pwd
import subprocess

from .config import get_config_value

def demote_to_user(user_name):
    def _demote():
        pw_record = pwd.getpwnam(user_name)
        os.setgid(pw_record.pw_gid)
        os.setuid(pw_record.pw_uid)
    return _demote

def _check_demoted(fn, shell_args, env=None):
    if env:
        passed_env = copy(os.environ)
        passed_env.update(env)
    else:
        passed_env = None
    return fn(shell_args, preexec_fn=demote_to_user(get_config_value('docker_user')), env=passed_env)

def check_call_demoted(shell_args, env=None):
    return _check_demoted(subprocess.check_call, shell_args, env)

def check_output_demoted(shell_args, env=None):
    return _check_demoted(subprocess.check_output, shell_args, env)
