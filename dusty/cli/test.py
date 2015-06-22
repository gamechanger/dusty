"""Allow you to run tests in an isolated container for an app or a lib.
If args are passed, default arguments are dropped

Usage:
  test <app_or_lib_name> [<suite_name>] [<args>...] [--recreate] [--no-pull]

Options:
  <suite_name>  Name of the test suite you would like to run
  <args>        A list of arguments to be passed to the test script
  --recreate    Ensures that the testing image will be recreated
  --no-pull     Do not pull dusty managed repos from remotes.

Examples:
  To call test suite frontend with default arguments:
    dusty test web frontend
  To call test suite frontend with arguments in place of the defaults:
    dusty test web frontend /web/javascript

"""

from docopt import docopt

from ..payload import Payload
from ..commands.test import (run_app_or_lib_tests, test_info_for_app_or_lib, pull_repos_and_sync_commands,
                             ensure_valid_suite_name)

def main(argv):
    args = docopt(__doc__, argv)
    if not args['<suite_name>']:
        return Payload(test_info_for_app_or_lib, args['<app_or_lib_name>'])
    else:
        payload0 = Payload(ensure_valid_suite_name, args['<app_or_lib_name>'], args['<suite_name>'])
        payload1 = Payload(pull_repos_and_sync_commands,
                           args['<app_or_lib_name>'],
                           pull_repos=not args['--no-pull'])
        payload2 = Payload(run_app_or_lib_tests,
                           args['<app_or_lib_name>'],
                           args['<suite_name>'],
                           args['<args>'],
                           force_recreate=args['--recreate'])
        payload2.run_on_daemon = False
        return [payload0, payload1, payload2]
