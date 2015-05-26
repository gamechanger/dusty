import subprocess
import logging

def call_command_from_client(shell_args, env=None):
    print "Running command: {}".format(' '.join(shell_args))
    try:
        subprocess.call(shell_args, env=env)
    except KeyboardInterrupt:
        print "KeyboardInterrupt; terminating"
        pass
