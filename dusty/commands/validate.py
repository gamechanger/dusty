import logging

from schemer import Schema

from ..compiler.spec_assembler import get_specs_path, get_specs_from_path
from ..schemas import app_schema

def validate_specs_from_path(specs_path):
    logging.info("Validating specs at path {}".format(specs_path))
    specs = get_specs_from_path(specs_path)
    for app in specs.get('apps', []).values():
        app_schema.validate(app)

def validate_specs():
    validate_specs_from_path(get_specs_path())
