import os

SOCKET_TERMINATOR = '\0\0'
SOCKET_ERROR_TERMINATOR = '\0\1'

LOCALHOST = "127.0.0.1"

SOCKET_LOGGER_NAME = 'socket_logger'

RUN_DIR = '/var/run/dusty'
SOCKET_PATH = os.path.join(RUN_DIR, 'dusty.sock')
FIRST_RUN_FILE_PATH = os.path.join(RUN_DIR, 'docker_first_time_started')

CONFIG_DIR = '/etc/dusty'
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.yml')
REPOS_DIR = os.path.join(CONFIG_DIR, 'repos')
COMPOSE_DIR = os.path.join(CONFIG_DIR, 'compose')
COMPOSEFILE_PATH = os.path.join(COMPOSE_DIR, 'docker-compose.yml')

NGINX_MAX_FILE_SIZE = "500M"

VM_PERSIST_DIR = '/persist'
VM_REPOS_DIR = os.path.join(VM_PERSIST_DIR, 'repos')

VM_CP_DIR = '/cp'
CONTAINER_CP_DIR = '/cp'

GIT_USER = 'git'

HOSTS_PATH = '/etc/hosts'

VIRTUALBOX_RULE_PREFIX = 'dusty'

SYSTEM_DEPENDENCY_VERSIONS = {
    'nginx': '1.8.0',
    'virtualbox': '4.3.26',
    'boot2docker': '1.6.0',
    'docker': '1.6.0',
    'docker-compose': '1.2.0'
}

CONFIG_SETTINGS = {
    'bundles': 'All currently activated bundles. These are the bundles that Dusty will set up for you when you run "dusty up".',
    'repo_overrides': 'All known repos for which Dusty will use your specified override instead of its own managed copy of the repository. You should override repos which you are actively developing so that Dusty uses your development version inside containers.',
    'mac_username': 'The user on the host OS who will own and be able to access the boot2docker VM. Dusty runs all VirtualBox, boot2docker, Docker, and Docker Compose commands as this user.',
    'specs_repo': 'This repository is used for storing the specs used by Dusty.  It is managed the same way as other repos',
    'nginx_includes_dir': 'This is the location that your nginx config will import extra files from.  Dusty\'s nginx config will be stored here',
    'setup_has_run': 'Key indicating if you have run the required command `dusty setup`'
}

WARN_ON_MISSING_CONFIG_KEYS = ['mac_username', 'specs_repo', 'nginx_includes_dir']
