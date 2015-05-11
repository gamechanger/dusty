import os
import logging

ROOT_LOG_DIR = '/var/log/dusty'
LOG_SUBDIRS = ['nginx']

def root_log_dir_is_writable():
    return os.access(ROOT_LOG_DIR, os.W_OK)

def ensure_log_subdirs_exist():
    for subdir in LOG_SUBDIRS:
        subdir_path = os.path.join(ROOT_LOG_DIR, subdir)
        if not os.path.exists(subdir_path):
            logging.info('Creating logging subdir {}'.format(subdir_path))
            os.mkdir(subdir_path)
