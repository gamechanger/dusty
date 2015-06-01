import os
import logging
import subprocess

from ... import constants
from ...config import get_config_value

def _get_nginx_pid():
    """Returns the current process ID of the master nginx process
    if it is running, otherwise False. Process IDs are positive
    integers, so we won't hit the truthiness issue with 0."""
    try:
        with open(constants.NGINX_PID_PATH, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 0) # Raises if process does not exist with this pid
        return pid
    except (IOError, OSError):
        return False

def _start_nginx():
    """Start a new nginx master process. This should not be called
    if nginx is already running. In that case, use _reload_nginx_config
    instead."""
    logging.info('Starting nginx')
    subprocess.check_call(['nginx'])

def _reload_nginx_config():
    """Reload the nginx master process to pick up the new config. We favor
    subprocess over sending a signal because it lets us know whether
    our new configuration is loaded successfully or not."""
    logging.info('Reloading nginx config')
    subprocess.check_call(['nginx', '-s', 'reload'])

def _ensure_nginx_running_with_latest_config():
    """Start nginx if it is not already running, or tell it to reload
    its configuration if it is."""
    if _get_nginx_pid():
        _reload_nginx_config()
    else:
        _start_nginx()

def _write_nginx_config(nginx_config):
    """Writes the config file from the Dusty Nginx compiler
    to the Nginx includes directory, which should be included
    in the main nginx.conf."""
    with open(os.path.join(get_config_value('nginx_includes_dir'), 'dusty.conf'), 'w') as f:
        f.write(nginx_config)

def update_nginx_from_config(nginx_config):
    """Write the given config to disk as a Dusty sub-config
    in the Nginx includes directory. Then, either start nginx
    or tell it to reload its config to pick up what we've
    just written."""
    logging.info('Updating nginx with new Dusty config')
    _write_nginx_config(nginx_config)
    _ensure_nginx_running_with_latest_config()
