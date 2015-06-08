"""Allow you to run tests in an isolated container for an app or a lib

Usage:
  test create_image <app_or_lib_name> [--recreate]

Options:
  --recreate  ensures that the testing image will be recreated

"""

from docopt import docopt

from ..commands.test import run_app_or_lib_tests

def main(argv):
    args = docopt(__doc__, argv)
    run_app_or_lib_tests(args['<app_or_lib_name>'], force_recreate=args['--recreate'])
