"""Stop containers associated with Dusty apps and services.

This does not remove the containers unless run with --rm-containers

Usage:
  stop [--rm-containers] [<services>...]

Options:
  --rm-containers  remove containers
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import stop_apps_or_services

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(stop_apps_or_services, args['<services>'], rm_containers=args['--rm-containers'])
