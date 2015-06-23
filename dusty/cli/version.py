"""Print Dusty daemon's current version

Usage:
  version
"""

from docopt import docopt

from ..payload import Payload
from ..commands.version import version

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(version)
