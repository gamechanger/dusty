import subprocess
import logging

def call_command_from_client(shell_args, env=None):
    logging.info("Running command: {}".format(' '.join(shell_args)))
    subprocess.call(shell_args, env=env)
