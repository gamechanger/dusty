
from ..compiler import compose, nginx, port_spec, spec_assembler

def start_local_env():
    """ This command will use the compilers to get compose specs
    will pass those specs to the systems that need them. Those
    systems will in turn launch the services needed to make the
    local environment go"""
    assembled_spec = spec_assembler.get_assembled_specs()
    port_spec = port_spec.get_port_spec_document(assembled_spec)
