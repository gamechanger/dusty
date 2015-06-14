"""Allow you to run tests in an isolated container for an app or a lib

Usage:
  test <app_or_lib_name> [<suite_name>] [<args>...] [--recreate]

Options:
  <suite_name>  Name of the test suite you would like to run
  <args>        A list of arguments to be passed to the test script
  --recreate    Ensures that the testing image will be recreated

"""

from docopt import docopt

from ..payload import Payload
from ..commands.test import run_app_or_lib_tests, test_info_for_app_or_lib

def main(argv):
    args = docopt(__doc__, argv)
    if not args['<suite_name>']:
        return Payload(test_info_for_app_or_lib, args['<app_or_lib_name>'])
    else:
        run_app_or_lib_tests(args['<app_or_lib_name>'], args['<suite_name>'], args['<args>'], force_recreate=args['--recreate'])
