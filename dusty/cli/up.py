"""Fully initialize all components of the Dusty system.

Up compiles your specs (subject to your activated bundles),
configures local port forwarding through your hosts file and
nginx, initializes your boot2docker VM and prepares it for
use by Dusty, and starts any containers specified by your
currently activated bundles.

Usage:
  up [--no-recreate] [--no-pull]

Options:
  --no-recreate   If a container already exists, do not recreate
                  it from scratch. This is faster, but containers
                  may get out of sync over time.

  --no-pull       Do not pull dusty managed repos from remotes.
                  Helpful if you do not have internet access.
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import start_local_env

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(start_local_env, recreate_containers=not args['--no-recreate'],
                   repull_repos=not args['--no-pull'])
