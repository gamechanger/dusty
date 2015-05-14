# Returns everything of type <dependent_type> that <name>, of type <root_spec_type> depends on
# Names only are returned in a set
def _get_dependent(dependent_type, name, specs, root_spec_type=None):
    if root_spec_type is None:
        root_spec_type = dependent_type
    spec = specs[root_spec_type].get(name)
    if name is None:
        raise RuntimeError("{} {} was referenced but not found".format(root_spec_type, name))
    dependents = spec.get('depends', {}).get(dependent_type, [])
    all_dependents = set(dependents)
    for dep in dependents:
        all_dependents |= _get_dependent(dependent_type, dep, specs)
    return all_dependents

# Returns a dictionary, with keys for each running app.  Values are dictionaries containing the
# app's spec, with additional downstream libs added to the depends.libs field
def get_active_app_info(activated_bundles, specs):
    compiled_apps = {}
    all_running_apps = set()
    for active_bundle in activated_bundles:
        bundle_spec = specs['bundles'].get(active_bundle)
        if bundle_spec is None:
            raise RuntimeError("Bundle {} is activated, but can't be found in your specs_path".format(active_bundle))
        for app_name in bundle_spec['apps']:
            all_running_apps.add(app_name)
            all_running_apps = all_running_apps | _get_dependent('apps', app_name, specs)
    for app_name in all_running_apps:
        compiled_apps[app_name] = specs['apps'][app_name]
        compiled_apps[app_name].get("depends", {})['libs'] = _get_dependent('libs', app_name, specs, 'apps')
    return compiled_apps

# Returns a set of the names of all services being run.
# Takes as input the output of get_active_app_info
def get_all_services(active_app_info):
    all_services = set()
    for spec in active_app_info.values():
        for service in spec.get('depends', {}).get('services', []):
            all_services.add(service)
    return all_services
