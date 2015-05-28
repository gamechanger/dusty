"""Output diagnostic data, useful for filing bug reports.

Usage:
  dump

Commands:
  dump    Output diagnostic data from your system.
"""

from docopt import docopt

from ..payload import Payload
from ..commands.dump import dump_diagnostics

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(dump_diagnostics)
