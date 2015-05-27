"""Fully initialize all components of the Dusty system. Containers
for activated bundles will be started.

Usage:
  up
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import start_local_env

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(start_local_env)
