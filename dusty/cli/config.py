"""Configure Dusty.

Usage:
  config list
  config listvalues
  config set <key> <value>
"""

from docopt import docopt

from ..payload import Payload
from ..commands.manage_config import list_config, list_config_values, save_value

def main(argv):
    args = docopt(__doc__, argv)
    if args['list']:
        return Payload(list_config)
    elif args['listvalues']:
        return Payload(list_config_values)
    elif args['set']:
        return Payload(save_value, args['<key>'], args['<value>'])
