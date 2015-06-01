"""Manage application bundles known to Dusty.

A bundle represents a set of applications that are
run together. Dusty uses your activated bundles as
an entrypoint to resolve which apps and services it
needs to run as part of your environment.

You can choose which bundles are activated to customize
your environment to what you're working on at the moment.
You don't need to run your entire stack all the time!

Usage:
  bundles activate <bundle_names>...
  bundles deactivate <bundle_names>...
  bundles list

Commands:
  activate     Activate one or more bundles.
  deactivate   Deactivate one or more bundles.
  list         List all bundles and whether they are currently active.
"""

from docopt import docopt

from ..payload import Payload
from ..commands.bundles import list_bundles, activate_bundle, deactivate_bundle

def main(argv):
    args = docopt(__doc__, argv)
    if args['list']:
        return Payload(list_bundles)
    elif args['activate']:
        return Payload(activate_bundle, args['<bundle_names>'])
    elif args['deactivate']:
        return Payload(deactivate_bundle, args['<bundle_names>'])
