"""Restart Dusty services.

Usage:
  restart [<services>...]
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import restart_apps_or_services

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(restart_apps_or_services, *args['<services>'])
