"""Give information on activated apps, services and
libs. Will present which ones are running in a
container and name to use when calling addressing them.

Usage:
  status
"""

from docopt import docopt

from ..payload import Payload
from ..commands.status import get_dusty_status

def main(argv):
    docopt(__doc__, argv)
    return Payload(get_dusty_status)
