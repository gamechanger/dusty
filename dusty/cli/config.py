"""Configure Dusty.

For a description of all available config keys,
run `config list`.

Usage:
  config list
  config listvalues
  config set <key> <value>

Commands:
  list          List all config keys with descriptions and current values.
  listvalues    List all config keys in machine-readable format.
  set           Set a string config key to a new value.
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
