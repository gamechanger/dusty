"""Restart containers associated with Dusty apps or services.

Upon restart, an app container will execute the command specified
in its `commands.always` spec key. Restarting app containers will
also perform a NFS mount of repos needed for restarted containers,
using your current repo override settings.

Usage:
  restart ( --repos <repos>... | [<services>...] )

Options:
  --repos <repos>   If provided, Dusty will restart any containers
                    that are using the repos specified.
  <services>        If provided, Dusty will only restart the given
                    services. Otherwise, all currently running
                    services are restarted.
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import restart_apps_or_services, restart_apps_by_repo

def main(argv):
    args = docopt(__doc__, argv)
    if args['--repos']:
        return Payload(restart_apps_by_repo, args['--repos'])
    return Payload(restart_apps_or_services, args['<services>'])
