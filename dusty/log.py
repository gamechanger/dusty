import os
import sys
import logging

from .constants import ROOT_LOG_DIR, LOG_SUBDIRS

def configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.captureWarnings(True)

def root_log_dir_is_writable():
    return os.access(ROOT_LOG_DIR, os.W_OK)

def ensure_log_subdirs_exist():
    for subdir in LOG_SUBDIRS:
        subdir_path = os.path.join(ROOT_LOG_DIR, subdir)
        if not os.path.exists(subdir_path):
            logging.info('Creating logging subdir {}'.format(subdir_path))
            os.mkdir(subdir_path)
