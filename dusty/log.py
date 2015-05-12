import sys
import logging

def configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.captureWarnings(True)
