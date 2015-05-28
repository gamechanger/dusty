"""Tail out Docker logs for a container running a Dusty application
or service.

Usage:
  logs tail <service>

Commands:
  tail    Tail the stdout/stderr output of a container.
"""

from docopt import docopt

from ..commands.logs import tail_container_logs

def main(argv):
    args = docopt(__doc__, argv)
    if args['tail']:
        return tail_container_logs(args['<service>'])
