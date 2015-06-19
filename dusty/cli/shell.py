"""Open a shell inside a running container. Works with Dusty
apps and services.

Usage:
  shell <service>

Example:
  To start a shell inside a container for a service named `website`:
    dusty shell website
"""

from docopt import docopt

from ..commands.shell import execute_shell
from ..payload import Payload

def main(argv):
    args = docopt(__doc__, argv)
    payload = Payload(execute_shell, args['<service>'])
    payload.run_on_daemon = False
    return payload
