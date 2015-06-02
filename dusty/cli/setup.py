"""Run this command once after installing dusty
to configure dusty to run properly.

Usage:
  setup [--mac_username=<mac_username>] [--default_specs_repo=<specs_repo>] [--nginx_includes_dir=<nginx_dir>]

Options:
  --mac_username=<mac_username>         mac_username daemon will run under
  --default_specs_repo=<specs_repo>     Repo where your dusty specs are located (eg github.com/gamechanger/dust)
  --nginx_includes_dir=<nginx_dir>      Path your nginx config looks in to load extra nginx configs
"""

from docopt import docopt
from ..commands.setup import setup_dusty_config

def main(argv):
    args = docopt(__doc__, argv)
    return setup_dusty_config(mac_username=args['--mac_username'],
                              specs_repo=args['--default_specs_repo'],
                              nginx_includes_dir=args['--nginx_includes_dir'])
