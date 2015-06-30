from prettytable import PrettyTable

from ..config import get_config_value, save_config_value
from ..compiler.spec_assembler import get_specs
from ..log import log_to_client
from .. import constants
from ..payload import daemon_command

@daemon_command
def list_bundles():
    specs, activated_bundles = get_specs(), get_config_value(constants.CONFIG_BUNDLES_KEY)
    table = PrettyTable(["Name", "Description", "Activated?"])
    for bundle, bundle_spec in specs[constants.CONFIG_BUNDLES_KEY].iteritems():
        table.add_row([bundle,
                       bundle_spec['description'],
                       "X" if bundle in activated_bundles else ""])
    log_to_client(table.get_string(sortby="Name"))

@daemon_command
def activate_bundle(bundle_names):
    specs = get_specs()
    for bundle_name in bundle_names:
        if bundle_name not in specs[constants.CONFIG_BUNDLES_KEY]:
            raise KeyError('No bundle exists named {}'.format(bundle_name))
    activated_bundles = set(get_config_value(constants.CONFIG_BUNDLES_KEY)).union(bundle_names)
    save_config_value(constants.CONFIG_BUNDLES_KEY, list(activated_bundles))
    log_to_client('Activated bundles {}'.format(', '.join(bundle_names)))

@daemon_command
def deactivate_bundle(bundle_names):
    specs = get_specs()
    for bundle_name in bundle_names:
        if bundle_name not in specs[constants.CONFIG_BUNDLES_KEY]:
            raise KeyError('No bundle exists named {}'.format(bundle_name))
    activated_bundles = set(get_config_value(constants.CONFIG_BUNDLES_KEY)).difference(bundle_names)
    save_config_value(constants.CONFIG_BUNDLES_KEY, list(activated_bundles))
    log_to_client('Deactivated bundles {}'.format(', '.join(bundle_names)))
