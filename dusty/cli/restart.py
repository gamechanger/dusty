"""Restart containers associated with Dusty apps or services.

Upon restart, an app container will execute the command specified
in its `commands.always` spec key. Restarting app containers will
also perform a sync of any local repos needed inside the container
prior to restarting.

Usage:
  restart [<services>...]
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import restart_apps_or_services

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(restart_apps_or_services, *args['<services>'])
