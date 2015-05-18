import os
import logging

PROCESS_ID = os.getpid()

def notify(message):
    # This will fail, among other things, if you try to call this function
    # on a non-OS X system (like Linux when we're running tests).
    # Also, the stupid library throws the exception on import, so we're
    # forced to do the import here.
    try:
        from pync import Notifier
        Notifier.notify(message, title='Dusty', group=PROCESS_ID)
    except:
        logging.exception('Exception when attempting to perform notification')
