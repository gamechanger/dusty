from ...source import Repo
from ...path import vm_command_files_path
from ... import constants

def get_command_files_volume_mount(app_or_lib_name, test=False):
    return "{}{}:{}".format(vm_command_files_path(app_or_lib_name), '/test' if test else '', constants.CONTAINER_COMMAND_FILES_DIR)

def get_asset_volume_mount(app_name):
    return "{}:{}".format(constants.VM_ASSETS_DIR, constants.IN_CONTAINER_ASSETS_DIR)

def get_volume_mounts(app_or_lib_name, assembled_specs, test=False):
    if app_or_lib_name in assembled_specs['apps']:
        return get_app_volume_mounts(app_or_lib_name, assembled_specs, test=test)
    elif app_or_lib_name in assembled_specs['libs']:
        return get_lib_volume_mounts(app_or_lib_name, assembled_specs)
    raise KeyError('{} is not an app or lib'.format(app_or_lib_name))

def get_app_volume_mounts(app_name, assembled_specs, test=False):
    """ This returns a list of formatted volume specs for an app. These mounts declared in the apps' spec
    and mounts declared in all lib specs the app depends on"""
    app_spec = assembled_specs['apps'][app_name]
    volumes = [get_command_files_volume_mount(app_name, test=test)]
    volumes.append(get_asset_volume_mount(app_name))
    repo_mount = _get_app_repo_volume_mount(app_spec)
    if repo_mount:
        volumes.append(repo_mount)
    volumes += _get_app_libs_volume_mounts(app_name, assembled_specs)
    return volumes

def get_lib_volume_mounts(base_lib_name, assembled_specs):
    """ Returns a list of the formatted volume specs for a lib"""
    volumes = [_get_lib_repo_volume_mount(assembled_specs['libs'][base_lib_name])]
    volumes.append(get_command_files_volume_mount(base_lib_name, test=True))
    for lib_name in assembled_specs['libs'][base_lib_name]['depends']['libs']:
        lib_spec = assembled_specs['libs'][lib_name]
        volumes.append(_get_lib_repo_volume_mount(lib_spec))
    return volumes

def _get_app_repo_volume_mount(app_spec):
    """ This returns the formatted volume mount spec to mount the local code for an app in the
    container """
    if app_spec['repo']:
        return "{}:{}".format(Repo(app_spec['repo']).vm_path, container_code_path(app_spec))

def _get_lib_repo_volume_mount(lib_spec):
    """ This returns the formatted volume mount spec to mount the local code for a lib in the
    container """
    return "{}:{}".format(Repo(lib_spec['repo']).vm_path, container_code_path(lib_spec))

def container_code_path(spec):
    """ Returns the path inside the docker container that a spec (for an app or lib) says it wants
    to live at """
    return spec['mount']

def _get_app_libs_volume_mounts(app_name, assembled_specs):
    """ Returns a list of the formatted volume mounts for all libs that an app uses """
    volumes = []
    for lib_name in assembled_specs['apps'][app_name]['depends']['libs']:
        lib_spec = assembled_specs['libs'][lib_name]
        volumes.append("{}:{}".format(Repo(lib_spec['repo']).vm_path, container_code_path(lib_spec)))
    return volumes
