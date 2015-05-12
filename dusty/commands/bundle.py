# coding=utf-8

from prettytable import PrettyTable

from ..config import get_config_value
from ..specs import get_specs

def list_bundles():
    specs, activated_bundles = get_specs(), get_config_value('bundles')
    table = PrettyTable(["Name", "Description", "Enabled?"])
    for bundle, bundle_spec in specs['bundles'].iteritems():
        table.add_row([bundle_spec['name'],
                       bundle_spec['description'],
                       u"✓" if bundle in activated_bundles else ""])
    return table.get_string(sortby="Name")
