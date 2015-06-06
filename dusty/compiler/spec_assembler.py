import os
import glob
import yaml
import logging

from ..config import get_config_value
from .. import constants
from ..source import Repo

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
    return set(get_config_value(constants.CONFIG_BUNDLES_KEY))

def _get_referenced_apps(specs):
    """
    Returns a set of all apps that are required to run any bundle in specs[constants.CONFIG_BUNDLES_KEY]
    """
    activated_bundles = specs[constants.CONFIG_BUNDLES_KEY].keys()
    all_active_apps = set()
    for active_bundle in activated_bundles:
        bundle_spec = specs[constants.CONFIG_BUNDLES_KEY].get(active_bundle)
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
        constants.CONFIG_BUNDLES_KEY: _get_active_bundles,
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
    _filter_active(constants.CONFIG_BUNDLES_KEY, specs)
    _filter_active('apps', specs)
    _expand_libs_in_apps(specs)
    _filter_active('libs', specs)
    _filter_active('services', specs)

def get_expected_number_of_running_containers():
    """ This will return the number of containers expected to be running based off of
    your current config"""
    assembled_specs = get_assembled_specs()
    return len(assembled_specs['apps']) + len(assembled_specs['services'])

def get_assembled_specs():
    logging.info("Spec Assembler: running...")
    specs = get_specs()
    _get_expanded_active_specs(specs)
    return specs

def get_specs_repo():
    return Repo(get_config_value(constants.CONFIG_SPECS_REPO_KEY))

def get_specs_path():
    return get_specs_repo().local_path

def get_specs():
    specs_path = get_specs_path()
    return get_specs_from_path(specs_path)

def get_repo_of_app_or_library(app_or_library_name):
    """ This function takes an app or library name and will return the corresponding repo
    for that app or library"""
    specs = get_specs()
    if app_or_library_name in specs['apps']:
        return Repo(specs['apps'][app_or_library_name]['repo'])
    elif app_or_library_name in specs['libs']:
        return Repo(specs['libs'][app_or_library_name]['repo'])
    raise KeyError('did not find app or service with name {}'.format(app_or_library_name))

def get_specs_from_path(specs_path):
    specs = {}
    for key in [constants.CONFIG_BUNDLES_KEY, 'apps', 'libs', 'services']:
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
                repos.add(Repo(spec['repo']))
    return repos
