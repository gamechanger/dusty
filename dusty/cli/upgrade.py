"""Upgrade Dusty's binaries

If Dusty is being run with a binary, this command will replace the
binary with the specified version from GitHub.  If no version is
specified, the latest version of the binary will be used.  The
daemon will then exec into the new version of the binary.

Usage:
  upgrade [<version>]

Options:
  <version>         If provided, this version of Dusty will be downloaded
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
