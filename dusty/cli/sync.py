"""Sync repos from the local filesystem to the boot2docker VM.

Usage:
  sync <repos>...
"""

from docopt import docopt

from ..payload import Payload
from ..commands.sync import sync_repos

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(sync_repos, **args['<repos>'])
