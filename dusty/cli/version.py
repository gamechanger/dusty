"""Print Dusty daemon's current version

Usage:
  version
"""

from docopt import docopt

from ..commands.version import version
from ..constants import VERSION
from ..payload import Payload

def main(argv):
    args = docopt(__doc__, argv)
    print 'Dusty client version: {}'.format(VERSION)
    return Payload(version)
