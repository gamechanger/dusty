"""Validates specs to ensure that they're consistent with specifications

Usage:
  validate [<specs-path>]
"""

from docopt import docopt

from ..payload import Payload
from ..commands.validate import validate_specs, validate_specs_from_path

def main(argv):
    args = docopt(__doc__, argv)
    if args['specs-path']:
        return Payload(validate_specs_from_path, args['specs-path'])
    else:
        return Payload(validate_specs)
