import os
import re

VERSION = '0.6.4'
BINARY = False # overridden by PyInstaller when we build a binary
PRERELEASE = False # overridden by PyInstaller when we build a prerelease binary

EXAMPLE_SPECS_REPO = 'github.com/gamechanger/dusty-example-specs'

DUSTY_CONFIG_BEGIN = '# BEGIN section for Dusty\n'
DUSTY_CONFIG_END = '# END section for Dusty\n'
DUSTY_CONFIG_REGEX = re.compile('\\{}.*\\{}'.format(DUSTY_CONFIG_BEGIN, DUSTY_CONFIG_END), flags=re.DOTALL | re.MULTILINE)
DUSTY_CONFIG_GROUP_REGEX = re.compile('.*\\{}(?P<dusty_config>.*)\\{}.*'.format(DUSTY_CONFIG_BEGIN, DUSTY_CONFIG_END), flags=re.DOTALL | re.MULTILINE)

SOCKET_ACK = '\1\1'
SOCKET_TERMINATOR = '\0\0'
SOCKET_ERROR_TERMINATOR = '\0\1'

SOCKET_LOGGER_NAME = 'socket_logger'

RUN_DIR = '/var/run/dusty'
SOCKET_PATH = os.getenv('DUSTY_SOCKET_PATH', os.path.join(RUN_DIR, 'dusty.sock'))

FIRST_RUN_FILE_PATH = '/.dusty_first_time_started'
CONTAINER_LOG_PATH = "/var/log"

CONFIG_DIR = '/etc/dusty'
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.yml')
REPOS_DIR = os.path.join(CONFIG_DIR, 'repos')
COMPOSE_DIR = os.path.join(CONFIG_DIR, 'compose')
COMPOSEFILE_PATH = os.path.join(COMPOSE_DIR, 'docker-compose.yml')
COMMAND_FILES_DIR = os.path.join(CONFIG_DIR, 'commands')

DUSTY_GITHUB_PATH = 'gamechanger/dusty'
DUSTY_BINARY_NAME = 'dusty'

VM_MACHINE_NAME = 'dusty'
VM_NIC_TYPE = 'Am79C973'

VM_PERSIST_DIR = '/persist'
VM_REPOS_DIR = '/dusty_repos'
LOCAL_BACKUP_DIR = 'dusty-backup'

VM_ASSETS_DIR = os.path.join(VM_PERSIST_DIR, 'dusty_assets')
IN_CONTAINER_ASSETS_DIR = '/dusty_assets'

DUSTY_NGINX_NAME = 'dustyInternalNginx'
NGINX_CONFIG_DIR_IN_VM = os.path.join(VM_PERSIST_DIR, 'dustyNginx')
NGINX_CONFIG_DIR_IN_CONTAINER = '/etc/nginx/conf.d'
NGINX_MAX_FILE_SIZE = "500M"
NGINX_IMAGE = "nginx:1.9.3"

NGINX_PRIMARY_CONFIG_NAME = 'nginx.primary'
NGINX_HTTP_CONFIG_NAME = 'dusty.http.conf'
NGINX_STREAM_CONFIG_NAME = 'dusty.stream.conf'

NGINX_BASE_CONFIG = """
user  nginx;
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

stream {
    include /etc/nginx/conf.d/*.stream.conf;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;

    keepalive_timeout  65;

    include /etc/nginx/conf.d/*.http.conf;
}
"""

VM_CP_DIR = '/cp'
CONTAINER_CP_DIR = '/cp'

VM_COMMAND_FILES_DIR = '/command_files'
CONTAINER_COMMAND_FILES_DIR = '/command_files'

GIT_USER = 'git'

HOSTS_PATH = '/etc/hosts'
EXPORTS_PATH = '/etc/exports'

VIRTUALBOX_RULE_PREFIX = 'dusty'

CONFIG_BUNDLES_KEY = 'bundles'
CONFIG_REPO_OVERRIDES_KEY = 'repo_overrides'
CONFIG_MAC_USERNAME_KEY = 'mac_username'
CONFIG_SPECS_REPO_KEY = 'specs_repo'
CONFIG_SETUP_KEY = 'setup_has_run'
CONFIG_ENV_KEY = 'dusty_env_overrides'
CONFIG_VM_MEM_SIZE = 'vm_memory_size'
CONFIG_CHANGESET_KEY = 'changeset'
CHANGESET_TESTING_KEY = 'testing_image'

CONFIG_SETTINGS = {
    CONFIG_BUNDLES_KEY: 'All currently activated bundles. These are the bundles that Dusty will set up for you when you run "dusty up".',
    CONFIG_REPO_OVERRIDES_KEY: 'All known repos for which Dusty will use your specified override instead of its own managed copy of the repository. You should override repos which you are actively developing so that Dusty uses your development version inside containers.',
    CONFIG_MAC_USERNAME_KEY: 'The user on the host OS who will own and be able to access the Docker VM. Dusty runs all VirtualBox, Docker, Docker Machine, and Docker Compose commands as this user.',
    CONFIG_SPECS_REPO_KEY: 'This repository is used for storing the specs used by Dusty.  It is managed the same way as other repos',
    CONFIG_SETUP_KEY: 'Key indicating if you have run the required command `dusty setup`',
    CONFIG_VM_MEM_SIZE: 'Specifies how much memory (in megabytes) you want your Docker VM to have',
    CONFIG_ENV_KEY: 'Environment overrides for apps and services that are specified with `dusty env`',
}

WARN_ON_MISSING_CONFIG_KEYS = [CONFIG_MAC_USERNAME_KEY, CONFIG_SPECS_REPO_KEY, CONFIG_VM_MEM_SIZE]
