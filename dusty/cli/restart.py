"""Restart containers associated with Dusty apps or services.

Upon restart, an app container will execute the command specified
in its `commands.always` spec key. Restarting app containers will
also perform a sync of any local repos needed inside the container
prior to restarting.

Usage:
  restart ( --repos <repos>... | [<services>...] ) [--no-sync]

Options:
  --no-sync         If provided, Dusty will not sync repos used by
                    services being restarted prior to the restart.
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
    common_args = {'sync': not args['--no-sync']}
    if args['--repos']:
        return Payload(restart_apps_by_repo, args['--repos'], **common_args)
    return Payload(restart_apps_or_services, args['<services>'], **common_args)
