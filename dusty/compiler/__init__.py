import pprint

from .spec_assembler import get_assembled_specs

def list_processed_specs():
    yield pprint.pformat(get_assembled_specs())
