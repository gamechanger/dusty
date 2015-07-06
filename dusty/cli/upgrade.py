"""Upgrade Dusty's binaries

Upgrades Dusty to the specified version.  If no version is
specified, this will upgrade to the latest version.  This command
only works if Dusty is being run as a binary (as opposed to running
from source).

Usage:
  upgrade [<version>]

Options:
  <version>     If provided, this version of Dusty will be downloaded
                and used (defaults to use the most recent version)
"""

from docopt import docopt

from ..payload import Payload
from ..commands.upgrade import upgrade_dusty_binary

def main(argv):
    args = docopt(__doc__, argv)
    if args['<version>']:
        return Payload(upgrade_dusty_binary, args['<version>'])
    return Payload(upgrade_dusty_binary)
