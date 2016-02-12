"""Allow you to run tests in an isolated container for an app or a lib.
If args are passed, default arguments are dropped

Usage:
  test [options] <app_or_lib_name> [<suite_name>] [<args>...]

Options:
  <suite_name>  Name of the test suite you would like to run
                If `all` is specified, all suites in the spec will be run
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
from ..commands.test import (run_one_suite, run_all_suites, test_info_for_app_or_lib, setup_for_test,
                             ensure_valid_suite_name, ensure_vm_initialized,
                             log_in_to_required_registries)

def main(argv):
    args = docopt(__doc__, argv, options_first=True)
    if args['<suite_name>'] == 'all':
        payload0 = Payload(ensure_vm_initialized)
        payload1 = Payload(log_in_to_required_registries, args['<app_or_lib_name>'])
        payload1.run_on_daemon = False
        payload2 = Payload(setup_for_test,
                           args['<app_or_lib_name>'],
                           pull_repos=not args['--no-pull'],
                           force_recreate=args['--recreate'])
        payload3 = Payload(run_all_suites,
                           args['<app_or_lib_name>'])
        payload3.run_on_daemon = False
        return [payload0, payload1, payload2, payload3]
    elif args['<suite_name>']:
        payload0 = Payload(ensure_valid_suite_name, args['<app_or_lib_name>'], args['<suite_name>'])
        payload1 = Payload(ensure_vm_initialized)
        payload2 = Payload(log_in_to_required_registries, args['<app_or_lib_name>'])
        payload2.run_on_daemon = False
        payload3 = Payload(setup_for_test,
                           args['<app_or_lib_name>'],
                           pull_repos=not args['--no-pull'],
                           force_recreate=args['--recreate'])
        payload4 = Payload(run_one_suite,
                           args['<app_or_lib_name>'],
                           args['<suite_name>'],
                           args['<args>'])
        payload4.run_on_daemon = False
        return [payload0, payload1, payload2, payload3, payload4]

    else:
        return Payload(test_info_for_app_or_lib, args['<app_or_lib_name>'])
