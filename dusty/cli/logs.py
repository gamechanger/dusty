"""Tail out Docker logs for a container running a Dusty application
or service.

Usage:
  logs [-f] [-t] [--tail=NUM] <service>

Options:
  -f          follow log output
  -t          show timestamps
  --tail=NUM  show NUM lines from end of file

"""
from docopt import docopt

from ..payload import Payload
from ..commands.logs import tail_container_logs

def main(argv):
    args = docopt(__doc__, argv)
    payload = Payload(tail_container_logs, args['<service>'], args['-f'], args['--tail'], args['-t'])
    payload.run_on_daemon = False
    return payload
