"""Run this command once after installing dusty
to configure dusty to run properly.

Usage:
  setup
"""

from docopt import docopt
from commands.setup import setup_dusty_config

def main(argv):
    docopt(__doc__, argv)
    return setup_dusty_config()
