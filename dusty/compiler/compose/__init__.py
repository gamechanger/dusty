from .. import get_assembled_specs
from ...config import get_config_value

def get_compiled_ports():
    return {}

def get_compose_dict():
    assembled_specs = get_assembled_specs()
    port_specs = get_compiled_ports()
    compose_dict = {}
    for app_name in assembled_specs['bundles'].keys():
        compose_dict[bundle_name] = composed_app_dict(app_name, assembled_specs, port_specs)
    specs_folder = get_config_value('specs_path')

def composed_app_dict(app_name, assembled_specs, port_specs):
    compose_bundle = {}
    compose_bundle['build'] = repo_directory(app_name, assembled_specs)

def repo_directory(app_name, assembled_specs):
    repo_overrides = get_config_value('repo_overrides')
    repo_name = assembled_specs['apps'][app_name]['repo']
    override_dir = repo_overrides.get(repo_name)
    return override_dir if override_dir else managed_repo_path(repo_name)
