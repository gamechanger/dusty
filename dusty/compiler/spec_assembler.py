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

def _filter_active_bundles(activated_bundles, specs):
    """
    Removes all bundles from specs['bundles'] that aren't in activated_bundles
    """
    all_bundles = specs['bundles'].keys()
    for bundle in all_bundles:
        if bundle not in activated_bundles:
            del specs['bundles'][bundle]

def _get_referenced_apps(specs):
    """
    Returns a set of all apps that are required to run any bundle in specs['bundles']
    """
    activated_bundles = specs['bundles'].keys()
    all_active_apps = set()
    for active_bundle in activated_bundles:
        bundle_spec = specs['bundles'].get(active_bundle)
        if bundle_spec is None:
            raise RuntimeError("Bundle {} is activated, but can't be found in your specs_path".format(active_bundle))
        for app_name in bundle_spec['apps']:
            all_active_apps.add(app_name)
            all_active_apps |= _get_dependent('apps', app_name, specs, 'apps')
    return all_active_apps

def _filter_active_apps(specs):
    """
    Removes all apps from specs['apps'] that aren't required by any bundle in specs['bundles']
    """
    active_apps = _get_referenced_apps(specs)
    all_apps = specs['apps'].keys()
    for app in all_apps:
        if app not in active_apps:
            del specs['apps'][app]

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

def _filter_active_libs(specs):
    """
    Removes any lib from specs['libs'] that isn't specified in any specs.apps.depends.libs field
    """
    active_libs = _get_referenced_libs(specs)
    all_libs = specs['libs'].keys()
    for lib in all_libs:
        if lib not in active_libs:
            del specs['libs'][lib]

def _get_referenced_services(specs):
    """
    Returns all services that are referenced in specs.apps.depends.services
    """
    active_services = set()
    for app_spec in specs['apps'].values():
        for service in app_spec.get('depends', {}).get('services', []):
            active_services.add(service)
    return active_services

def _filter_active_services(specs):
    """
    Removes any service from specs['services'] that isn't specified in any specs.apps.depends.services
    """
    active_services = _get_referenced_services(specs)
    all_services = specs['services'].keys()
    for service in all_services:
        if service not in active_services:
            del specs['services'][service]

def _get_expanded_active_specs(activated_bundles, specs):
    """
    This function removes any unnecessary bundles, apps, libs, and services that aren't needed by
    the activated_bundles.  It also expands inside specs.apps.depends.libs all libs that are needed
    indirectly by each app
    """
    _filter_active_bundles(activated_bundles, specs)
    _filter_active_apps(specs)
    _expand_libs_in_apps(specs)
    _filter_active_libs(specs)
    _filter_active_services(specs)

def get_assembled_specs():
    activated_bundles = set(get_config_value('bundles'))
    specs = get_specs()
    _get_expanded_active_specs(activated_bundles, specs)
    return specs

