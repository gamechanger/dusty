import os

from pync import Notifier

PROCESS_ID = os.getpid()

def notify(message):
    Notifier.notify(message, title='Dusty', group=PROCESS_ID)
