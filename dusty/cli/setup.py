"""Run this command once after installation to set up
configuration values tailored to your system.

Usage:
  setup [--mac_username=<mac_username>] [--default_specs_repo=<specs_repo>] [--nginx_includes_dir=<nginx_dir>]

Options:
  --mac_username=<mac_username>         User name of the primary Dusty client user. This user
                                        will own all Docker-related processes.
  --default_specs_repo=<specs_repo>     Repo where your Dusty specs are located. Dusty manages this
                                        repo for you just like other repos.
  --nginx_includes_dir=<nginx_dir>      Directory in which Dusty will write its nginx config. Your
                                        nginx master config should source files from this directory
                                        using an `includes` directive.
"""

from docopt import docopt
from ..payload import Payload
from ..commands.setup import setup_dusty_config

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(setup_dusty_config, mac_username=args['--mac_username'],
                              specs_repo=args['--default_specs_repo'],
                              nginx_includes_dir=args['--nginx_includes_dir'],
                              run_on_daemon=False)
