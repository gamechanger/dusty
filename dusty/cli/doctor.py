"""Attempt to fix networking issues with your Dusty VM

VirtualBox can get itself in a state where the network between
your host Mac and the Dusty VM stops functioning. This command
automatically tries a few debugging commands which are known
to fix the networking bugs in certain situations.

Usage:
  doctor
"""

from docopt import docopt

from ..payload import Payload
from ..commands.doctor import run_doctor

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(run_doctor)
