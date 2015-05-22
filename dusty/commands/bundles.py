# coding=utf-8

from prettytable import PrettyTable

from ..config import get_config_value, save_config_value
from ..compiler.spec_assembler import get_specs

def list_bundles():
    specs, activated_bundles = get_specs(), get_config_value('bundles')
    table = PrettyTable(["Name", "Description", "Enabled?"])
    for bundle, bundle_spec in specs['bundles'].iteritems():
        table.add_row([bundle,
                       bundle_spec['description'],
                       u"✓" if bundle in activated_bundles else ""])
    yield table.get_string(sortby="Name")

def activate_bundle(bundle_name):
    specs = get_specs()
    if bundle_name not in specs['bundles']:
        raise KeyError('No bundle exists named {}'.format(bundle_name))
    activated_bundles = set(get_config_value('bundles'))
    if bundle_name not in activated_bundles:
        activated_bundles.add(bundle_name)
        save_config_value('bundles', list(activated_bundles))
    yield 'Activated bundle {}'.format(bundle_name)

def deactivate_bundle(bundle_name):
    specs = get_specs()
    if bundle_name not in specs['bundles']:
        raise KeyError('No bundle exists named {}'.format(bundle_name))
    activated_bundles = set(get_config_value('bundles'))
    if bundle_name in activated_bundles:
        activated_bundles.remove(bundle_name)
        save_config_value('bundles', list(activated_bundles))
    yield 'Deactivated bundle {}'.format(bundle_name)
