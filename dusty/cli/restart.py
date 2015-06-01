"""Restart containers associated with Dusty apps or services.

Upon restart, an app container will execute the command specified
in its `commands.always` spec key. Restarting app containers will
also perform a sync of any local repos needed inside the container
prior to restarting.

Usage:
  restart [--no-sync] [<services>...]

Options:
  --no-sync    If provided, Dusty will not sync repos used by
               services being restarted prior to the restart.
  <services>   If provided, Dusty will only restart the given
               services. Otherwise, all currently running
               services are restarted.
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import restart_apps_or_services

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(restart_apps_or_services, args['<services>'], sync=not args['--no-sync'])
