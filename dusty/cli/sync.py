"""Sync repos from the local filesystem to the boot2docker VM.

Sync uses rsync under the hood to quickly sync files between
your local filesystem and the boot2docker VM. Sync will use
either the Dusty-managed version of a repo or your overridden
version, depending on the current repo settings.

Usage:
  sync <repos>...
"""

from docopt import docopt

from ..payload import Payload
from ..commands.sync import sync_repos

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(sync_repos, **args['<repos>'])
