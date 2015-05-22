import os
import glob
import yaml
import logging

from ..config import get_config_value, assert_config_key
from ..source import repo_path


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

def _filter_active(spec_type, specs):
    get_referenced = {
        'bundles': _get_active_bundles,
        'apps': _get_referenced_apps,
        'libs': _get_referenced_libs,
        'services': _get_referenced_services
    }
    active = get_referenced[spec_type](specs)
    all_specs = specs[spec_type].keys()
    for item_name in all_specs:
        if item_name not in active:
            del specs[spec_type][item_name]
    logging.info("Spec Assembler: filtered active {} to {}".format(spec_type, set(specs[spec_type].keys())))

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

def get_specs_repo():
    assert_config_key('specs_repo')
    return get_config_value('specs_repo')

def get_specs_path():
    return repo_path(get_specs_repo())

def get_specs():
    specs_path = get_specs_path()
    return get_specs_from_path(specs_path)

def get_specs_from_path(specs_path):
    specs = {}
    for key in ['bundles', 'apps', 'libs', 'services']:
        specs[key] = {}
        key_path = os.path.join(specs_path, key)
        for spec_path in glob.glob('{}/*.yml'.format(key_path)):
            spec_name = os.path.splitext(os.path.split(spec_path)[-1])[0]
            with open(spec_path, 'r') as f:
                specs[key][spec_name] = yaml.load(f.read())
    return specs

def get_all_repos(active_only=False, include_specs_repo=True):
    repos = set()
    if include_specs_repo:
        repos.add(get_specs_repo())
    specs = get_assembled_specs() if active_only else get_specs()
    for type_key in ['apps', 'libs']:
        for spec in specs[type_key].itervalues():
            if 'repo' in spec:
                repos.add(spec['repo'])
    return repos
