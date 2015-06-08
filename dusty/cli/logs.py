"""Tail out Docker logs for a container running a Dusty application
or service.

Usage:
  logs [-f] [--tail=NUM] <service>

Options:
  -f          follow log output
  --tail=NUM  show NUM lines from end of file

"""
from docopt import docopt

from ..commands.logs import tail_container_logs

def main(argv):
    args = docopt(__doc__, argv)
    return tail_container_logs(args['<service>'], args['-f'], args['--tail'])
