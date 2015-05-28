"""Manage application bundles known to Dusty.

Usage:
  bundles list
  bundles activate <bundle_name>
  bundles deactivate <bundle_name>
"""

from docopt import docopt

from ..payload import Payload
from ..commands.bundles import list_bundles, activate_bundle, deactivate_bundle

def main(argv):
    args = docopt(__doc__, argv)
    if args['list']:
        return Payload(list_bundles)
    elif args['activate']:
        return Payload(activate_bundle, args['<bundle_name>'])
    elif args['deactivate']:
        return Payload(deactivate_bundle, args['<bundle_name>'])
