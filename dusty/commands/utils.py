import os
import subprocess

def _executable_path(executable_name):
    return subprocess.check_output(['which', executable_name]).strip()

def exec_docker(*args):
    os.execl(_executable_path('docker'), 'docker', *args)
