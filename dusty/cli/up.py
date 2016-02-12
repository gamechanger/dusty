"""Fully initialize all components of the Dusty system.

Up compiles your specs (subject to your activated bundles),
configures local port forwarding through your hosts file and
nginx, initializes your Docker VM and prepares it for
use by Dusty, and starts any containers specified by your
currently activated bundles.

Usage:
  up [--no-recreate] [--no-pull]

Options:
  --no-recreate   If a container already exists, do not recreate
                  it from scratch. This is faster, but containers
                  may get out of sync over time.
  --no-pull       Do not pull dusty managed repos from remotes.
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import (prep_for_start_local_env,
                            log_in_to_required_registries,
                            start_local_env)

def main(argv):
    args = docopt(__doc__, argv)
    payload0 = Payload(prep_for_start_local_env, pull_repos=not args['--no-pull'])
    payload1 = Payload(log_in_to_required_registries)
    payload1.run_on_daemon = False
    payload2 = Payload(start_local_env, recreate_containers=not args['--no-recreate'])
    return [payload0, payload1, payload2]
