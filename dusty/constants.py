import os

ROOT_LOG_DIR = '/var/log/dusty'
LOG_SUBDIRS = ['nginx']

SOCKET_PATH = '/var/run/dusty/dusty.sock'
CONFIG_PATH = '/var/run/dusty/config.yml'

SYSTEM_DEPENDENCY_VERSIONS = {
    'nginx': '1.8.0',
    'virtualbox': '4.3.26',
    'boot2docker': '1.6.0',
    'docker': '1.6.0'
}
