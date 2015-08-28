"""
Place files in Dusty containers

Assets are files to be put in containers, but which don't live in a repository.
Assets are declared in Dusty specs of apps and libraries, and their values are
managed with the CLI.

Usage:
    assets list [<app_or_lib>]
    assets read <asset_key>
    assets set <asset_key> <local_path>
    assets unset <asset_key>

Commands:
    list        List all assets that are defined in specs for active apps and libs
    read        Print the current value of an asset
    set         Associate an asset with the contents of a local file
    unset       Delete the currently registered value of an asset

Examples:
    To set the value of the asset GITHUB_KEY to the contents of ~/.ssh/id_rsa:
        dusty assets set GITHUB_KEY ~/.ssh/id_rsa
"""

import os
import sys

from docopt import docopt

from ..payload import Payload
from ..commands import assets
from ..log import log_to_client

def main(argv):
    args = docopt(__doc__, argv)
    if args['list']:
        if args['<app_or_lib>']:
            assets.list_by_app_or_lib(args['<app_or_lib>'])
        else:
            assets.list_all()
    elif args['read']:
        assets.read_asset(args['<asset_key>'])
    elif args['set']:
        if not os.access(args['<local_path>'], os.R_OK):
            log_to_client('Local path {} does not exist, or you don\'t have permission to access it'.format(args['<local_path>']))
            sys.exit(1)
        assets.set_asset(args['<asset_key>'], os.path.abspath(args['<local_path>']))
    elif args['unset']:
        assets.unset_asset(args['<asset_key>'])
