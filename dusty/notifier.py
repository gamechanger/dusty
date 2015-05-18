import os
import logging

from pync import Notifier

PROCESS_ID = os.getpid()

def notify(message):
    # This will fail, among other things, if you try to call this function
    # on a non-OS X system (like Linux when we're running tests)
    try:
        Notifier.notify(message, title='Dusty', group=PROCESS_ID)
    except:
        logging.exception('Exception when attempting to perform notification')
