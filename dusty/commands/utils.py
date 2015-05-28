import subprocess

def _executable_path(executable_name):
    return subprocess.check_output(['which', executable_name]).strip()
