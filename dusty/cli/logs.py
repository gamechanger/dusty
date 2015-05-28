"""Tail out Docker logs for a Dusty process.

Usage:
  logs tail <service>
"""

from docopt import docopt

from ..commands.logs import tail_container_logs

def main(argv):
    args = docopt(__doc__, argv)
    if args['tail']:
        return tail_container_logs(args['<service>'])
