"""Run this command once after installation to set up
configuration values tailored to your system.

Usage:
  setup [options]

Options:
  --mac_username=<mac_username>          User name of the primary Dusty client user. This user
                                         will own all Docker-related processes.
  --default_specs_repo=<specs_repo>      Repo where your Dusty specs are located. Dusty manages this
                                         repo for you just like other repos.
  --vm_memory=<memory_mb>                Memory to assign to the Docker VM, in megabytes
  --no-update                            Skip pulling managed repos at conclusion of setup
"""

from docopt import docopt
from ..payload import Payload
from ..commands.setup import setup_dusty_config

def main(argv):
    args = docopt(__doc__, argv)
    return setup_dusty_config(mac_username=args['--mac_username'],
                              specs_repo=args['--default_specs_repo'],
                              vm_memory=args['--vm_memory'],
                              update=not args['--no-update'])
