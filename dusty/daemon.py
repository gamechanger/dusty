import sys
import logging

from .preflight import preflight_check
from .notifier import notify

def configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.captureWarnings(True)

def main():
    notify('Dusty initializing...')
    configure_logging()
    preflight_check()

if __name__ == '__main__':
    main()
