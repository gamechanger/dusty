"""Shut down the Dusty VM.

Usage:
  shutdown
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import shutdown_dusty_vm

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(shutdown_dusty_vm)
