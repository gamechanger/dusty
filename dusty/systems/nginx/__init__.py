import os
import logging
import subprocess

from ... import constants
from ...config import get_config_value

def _start_nginx():
    """Start a new nginx master process. This should not be called
    if nginx is already running. In that case, use _stop_nginx first"""
    logging.info('Starting nginx')
    subprocess.check_call(['nginx'])

def _reload_nginx_config():
    """Relaod the config for the nginx master process."""
    logging.info('Reloading nginx config')
    subprocess.check_call(['nginx', '-s', 'reload'])

def _ensure_nginx_running_with_latest_config():
    """Start nginx if it is not already running, or restart the
    process if it is already running."""
    try:
        _reload_nginx_config()
    except:
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
