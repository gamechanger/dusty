# coding=utf-8

from prettytable import PrettyTable

from ..config import get_config_value, save_config_value
from ..compiler.spec_assembler import get_specs
from ..log import log_to_client

def list_bundles():
    specs, activated_bundles = get_specs(), get_config_value('bundles')
    table = PrettyTable(["Name", "Description", "Enabled?"])
    for bundle, bundle_spec in specs['bundles'].iteritems():
        table.add_row([bundle,
                       bundle_spec['description'],
                       u"✓" if bundle in activated_bundles else ""])
    log_to_client(table.get_string(sortby="Name"))

def activate_bundle(bundle_names):
    specs = get_specs()
    for bundle_name in bundle_names:
        if bundle_name not in specs['bundles']:
            raise KeyError('No bundle exists named {}'.format(bundle_name))
    activated_bundles = set(get_config_value('bundles')).union(bundle_names)
    save_config_value('bundles', list(activated_bundles))
    log_to_client('Activated bundles {}'.format(', '.join(bundle_names)))

def deactivate_bundle(bundle_names):
    specs = get_specs()
    for bundle_name in bundle_names:
        if bundle_name not in specs['bundles']:
            raise KeyError('No bundle exists named {}'.format(bundle_name))
    activated_bundles = set(get_config_value('bundles')).difference(bundle_names)
    save_config_value('bundles', list(activated_bundles))
    log_to_client('Deactivated bundles {}'.format(', '.join(bundle_names)))
