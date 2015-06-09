"""Execute scripts defined in an app's spec inside a running app container.

Usage:
  scripts <app_name> [<script_name>] [<args>...]

Options:
  <args>  Arguments to pass to the script

Examples:
  To get information on all scripts available for an app called `website`:
    dusty script website

  To run the `rebuild` script defined inside the `website` app spec:
    dusty script website rebuild
"""

from docopt import docopt

from ..payload import Payload
from ..commands.script import script_info_for_app, execute_script

def main(argv):
    args = docopt(__doc__, argv)
    if not args['<script_name>']:
        return Payload(script_info_for_app, args['<app_name>'])
    else:
        return execute_script(args['<app_name>'], args['<script_name>'], script_arguments=args['<args>'])
