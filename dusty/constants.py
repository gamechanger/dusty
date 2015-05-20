import os

SOCKET_TERMINATOR = '\0\0'
SOCKET_ERROR_TERMINATOR = '\0\1'

LOCALHOST = "127.0.0.1"

ROOT_LOG_DIR = '/var/log/dusty'
LOG_SUBDIRS = ['nginx']

RUN_DIR = '/var/run/dusty'
SOCKET_PATH = os.path.join(RUN_DIR, 'dusty.sock')
FIRST_RUN_FILE_PATH = os.path.join(RUN_DIR, 'docker_first_time_started')

CONFIG_DIR = '/etc/dusty'
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.yml')
REPOS_DIR = os.path.join(CONFIG_DIR, 'repos')
COMPOSE_DIR = os.path.join(CONFIG_DIR, 'compose')

GIT_USER = 'git'

HOSTS_PATH = '/etc/hosts'

VIRTUALBOX_RULE_PREFIX = 'dusty'

NGINX_PID_PATH = '/usr/local/var/run/nginx.pid'
NGINX_CONFIG_INCLUDES_DIR = '/usr/local/etc/nginx/servers'

SYSTEM_DEPENDENCY_VERSIONS = {
    'nginx': '1.8.0',
    'virtualbox': '4.3.26',
    'boot2docker': '1.6.0',
    'docker': '1.6.0'
}

CONFIG_SETTINGS = {
    'bundles': 'All currently activated bundles. These are the bundles that Dusty will set up for you when you run "dusty up".',
    'repo_overrides': 'All known repos for which Dusty will use your specified override instead of its own managed copy of the repository. You should override repos which you are actively developing so that Dusty uses your development version inside containers.',
    'mac_username': 'The user on the host OS who will own and be able to access the boot2docker VM. Dusty runs all VirtualBox, boot2docker, Docker, and Docker Compose commands as this user.',
    'specs_path': 'About to be deleted...'
}
