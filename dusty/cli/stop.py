"""Stop containers associated with Dusty apps and services.

Usage:
  stop <services>...
"""

from docopt import docopt

from ..payload import Payload
from ..commands.run import stop_apps_or_services

def main(argv):
    args = docopt(__doc__, argv)
    return Payload(stop_apps_or_services, *args['<services>'])
