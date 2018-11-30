import os
import sys
import re

from pkg_resources import resource_string

VERSION = '0.7.4'
BINARY = False # overridden by PyInstaller when we build a binary
PRERELEASE = False # overridden by PyInstaller when we build a prerelease binary

EXAMPLE_SPECS_REPO = 'github.com/gamechanger/dusty-example-specs'

PUBLIC_DOCKER_REGISTRY = 'index.docker.io'
DOCKER_CONFIG_PATH = os.path.expanduser('~/.docker/config.json')

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

DAEMON_HTTP_BIND_IP = '127.0.0.1'
DAEMON_HTTP_BIND_PORT = 60912

FILE_HANDLE_LIMIT = 8192

FIRST_RUN_FILE_PATH = '/.dusty_first_time_started'
CONTAINER_LOG_PATH = "/var/log"

CONFIG_DIR = '/Users/jhsu/work/dusty_root'
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.yml')
PERSIST_DIR = os.path.join(CONFIG_DIR, 'persist')
REPOS_DIR = os.path.join(CONFIG_DIR, 'repos')
COMPOSE_DIR = os.path.join(CONFIG_DIR, 'compose')
COMPOSEFILE_PATH = os.path.join(COMPOSE_DIR, 'docker-compose.yml')
COMMAND_FILES_DIR = os.path.join(CONFIG_DIR, 'commands')

DUSTY_GITHUB_PATH = 'gamechanger/dusty'
DUSTY_BINARY_NAME = 'dusty'

VM_MACHINE_NAME = 'dusty'
VM_NIC_TYPE = 'Am79C973'

VM_PERSIST_DIR = PERSIST_DIR
VM_REPOS_DIR = REPOS_DIR
# VM_PERSIST_DIR = '/persist'
# VM_REPOS_DIR = '/dusty_repos'
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
NGINX_502_PAGE_NAME = 'dusty_custom_502.html'

NGINX_BASE_CONFIG = resource_string(__name__, 'resources/nginx_base_config.txt')
NGINX_502_PAGE_HTML_TEMPLATE = resource_string(__name__, 'resources/nginx_502_page.html')

# Inline JS and CSS resources in our 502 HTML
NGINX_502_PAGE_HTML = NGINX_502_PAGE_HTML_TEMPLATE.format(jquery_source=resource_string(__name__, 'resources/jquery-2.2.1.min.js'),
                                                          skeleton_source=resource_string(__name__, 'resources/skeleton.min.css'),
                                                          custom_js_source=resource_string(__name__, 'resources/502.js'))

# VM_CP_DIR = '/cp'
VM_CP_DIR = os.path.join(CONFIG_DIR, 'cp')
CONTAINER_CP_DIR = '/cp'

# VM_COMMAND_FILES_DIR = '/command_files'
VM_COMMAND_FILES_DIR = COMMAND_FILES_DIR
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
