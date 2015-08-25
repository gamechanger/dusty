"""Set environment variable overrides.

Environment variables specified will be added to app
and service container environments, overriding variables
specified in a `compose.env` spec (if present).

Usage:
  env list [<app_or_service>]
  env set <app_or_service> (<var_name> <value> | --file <local_file>)
  env unset <app_or_service> (--all | <var_name>)

Commands:
  list        List all environment variables and their current values.
  set         Set a variable name to a new value for the given app or service.
  unset       Unset a variable for the given app or service.
"""
import os

from docopt import docopt

from ..payload import Payload
from ..commands import env

def main(argv):
    args = docopt(__doc__, argv)
    if args['list']:
        if args['<app_or_service>']:
            return Payload(env.list_app_or_service, args['<app_or_service>'])
        else:
            return Payload(env.list_all)
    elif args['set']:
        if args['--file']:
            return Payload(env.set_from_file, args['<app_or_service>'], os.path.abspath(args['<local_file>']))
        else:
            return Payload(env.set_var, args['<app_or_service>'], args['<var_name>'], args['<value>'])
    elif args['unset']:
        if args['--all']:
            return Payload(env.unset_all, args['<app_or_service>'])
        else:
            return Payload(env.unset_var, args['<app_or_service>'], args['<var_name>'])
