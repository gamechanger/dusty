import pprint


from .process_bundle import get_expanded_active_specs
from ..specs import get_specs
from ..config import get_config_value

def list_processed_specs():
    activated_bundles = set(get_config_value('bundles'))
    specs = get_specs()
    processed_specs = get_expanded_active_specs(activated_bundles, specs)
    yield pprint.pformat(processed_specs)
