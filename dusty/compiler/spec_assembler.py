import logging

from ..config import get_config_value
from ..specs import get_specs


def _get_dependent(dependent_type, name, specs, root_spec_type):
    """
    Returns everything of type <dependent_type> that <name>, of type <root_spec_type> depends on
    Names only are returned in a set
    """
    spec = specs[root_spec_type].get(name)
    if spec is None:
        raise RuntimeError("{} {} was referenced but not found".format(root_spec_type, name))
    dependents = spec.get('depends', {}).get(dependent_type, [])
    all_dependents = set(dependents)
    for dep in dependents:
        all_dependents |= _get_dependent(dependent_type, dep, specs, dependent_type)
    return all_dependents

def _get_active_bundles(specs):
    return set(get_config_value('bundles'))

def _get_referenced_apps(specs):
    """
    Returns a set of all apps that are required to run any bundle in specs['bundles']
    """
    activated_bundles = specs['bundles'].keys()
    all_active_apps = set()
    for active_bundle in activated_bundles:
        bundle_spec = specs['bundles'].get(active_bundle)
        for app_name in bundle_spec['apps']:
            all_active_apps.add(app_name)
            all_active_apps |= _get_dependent('apps', app_name, specs, 'apps')
    return all_active_apps

def _expand_libs_in_apps(specs):
    """
    Expands specs.apps.depends.libs to include any indirectly required libs
    """
    for app_name, app_spec in specs['apps'].iteritems():
        if 'depends' in app_spec and 'libs' in app_spec['depends']:
            app_spec['depends']['libs'] = _get_dependent('libs', app_name, specs, 'apps')

def _get_referenced_libs(specs):
    """
    Returns all libs that are referenced in specs.apps.depends.libs
    """
    active_libs = set()
    for app_spec in specs['apps'].values():
        for lib in app_spec.get('depends', {}).get('libs', []):
            active_libs.add(lib)
    return active_libs

def _get_referenced_services(specs):
    """
    Returns all services that are referenced in specs.apps.depends.services
    """
    active_services = set()
    for app_spec in specs['apps'].values():
        for service in app_spec.get('depends', {}).get('services', []):
            active_services.add(service)
    return active_services

def _filter_active(type, specs):
    get_referenced = {
        'bundles': _get_active_bundles,
        'apps': _get_referenced_apps,
        'libs': _get_referenced_libs,
        'services': _get_referenced_services
    }
    active = get_referenced[type](specs)
    all_type = specs[type].keys()
    for item_name in all_type:
        if item_name not in active:
            del specs[type][item_name]
    logging.info("Spec Assembler: filtered active {} to {}".format(type, set(specs[type].keys())))

def _get_expanded_active_specs(specs):
    """
    This function removes any unnecessary bundles, apps, libs, and services that aren't needed by
    the activated_bundles.  It also expands inside specs.apps.depends.libs all libs that are needed
    indirectly by each app
    """
    _filter_active('bundles', specs)
    _filter_active('apps', specs)
    _expand_libs_in_apps(specs)
    _filter_active('libs', specs)
    _filter_active('services', specs)

def get_assembled_specs():
    logging.info("Spec Assembler: running...")
    specs = get_specs()
    _get_expanded_active_specs(specs)
    return specs

