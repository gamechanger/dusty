import logging

import yaml

from .. import get_assembled_specs
from ...source import repo_path
from ..port_spec import port_spec_document
from ... import constants

def get_compose_dict(assembled_specs, port_specs):
    compose_dict = {}
    for app_name in assembled_specs['apps'].keys():
        compose_dict[app_name] = _composed_app_dict(app_name, assembled_specs, port_specs)
    for service_name in assembled_specs.get('services', []):
        compose_dict[service_name] = _composed_service_dict(service_name, assembled_specs)
    return compose_dict

def _composed_app_dict(app_name, assembled_specs, port_specs):
    logging.info("Compiling compose dict for app {}".format(app_name))
    app_spec = assembled_specs['apps'][app_name]
    compose_dict = app_spec.get("compose", {})
    if 'image' in app_spec and 'build' in app_spec:
        raise RuntimeError("image and build are both specified in the spec for {}".format(app_name))
    elif 'image' in app_spec:
        logging.info
        compose_dict['image'] = app_spec['image']
    elif 'build' in app_spec:
        compose_dict['build'] = app_spec['build']
    else:
        raise RuntimeError("Neither image nor build was specified in the spec for {}".format(app_name))
    compose_dict['command'] = _compile_docker_command(app_name, assembled_specs)
    compose_dict['links'] = app_spec.get('depends', {}).get('services', []) + app_spec.get('depends', {}).get('apps', [])
    compose_dict['volumes'] = _get_compose_volumes(app_name, assembled_specs)
    port_list = _get_ports_list(app_name, port_specs)
    if port_list:
        compose_dict['ports'] = port_list
    return compose_dict

def _composed_service_dict(service_name, assembled_specs):
    return assembled_specs['services'][service_name]

def _get_ports_list(app_name, port_specs):
    if app_name not in port_specs['docker_compose']:
        return []
    return ["{}:{}".format(port_spec['mapped_host_port'],
        port_spec['in_container_port']) for port_spec in port_specs['docker_compose'][app_name]]

def _compile_docker_command(app_name, assembled_specs):
    app_spec = assembled_specs['apps'][app_name]
    first_run_file = constants.FIRST_RUN_FILE_PATH
    command = []
    command += _lib_install_commands_for_app(app_name, assembled_specs)
    command.append("export PATH=$PATH:{}".format(_container_code_path(app_spec)))
    command.append("if [ ! -f {} ]".format(first_run_file))
    once_command = app_spec['commands'].get("once", "")
    command.append("then touch {}".format(first_run_file))
    if once_command:
        command.append(once_command)
    command.append("fi")
    command.append(app_spec['commands']['always'])
    return "sh -c \"{}\"".format('; '.join(command))

def _lib_install_commands_for_app(app_name, assembled_specs):
    libs = assembled_specs['apps'][app_name].get('depends', {}).get('libs', [])
    commands = []
    for lib in libs:
        lib_spec = assembled_specs['libs'][lib]
        commands.append(_lib_install_command(lib_spec))
    return commands

def _lib_install_command(lib_spec):
    lib_dir = lib_spec['mount']
    install_command = lib_spec['install']
    return "cd {} && {}".format(lib_dir, install_command)

def _get_compose_volumes(app_name, assembled_specs):
    app_spec = assembled_specs['apps'][app_name]
    volumes = []
    volumes.append(_get_app_volume_mount(app_spec))
    volumes += _get_libs_volume_mounts(app_name, assembled_specs)
    return volumes

def _get_app_volume_mount(app_spec):
    app_repo_path = repo_path(app_spec['repo'])
    return "{}:{}".format(app_repo_path, _container_code_path(app_spec))

def _container_code_path(spec):
    return spec['mount']

def _get_libs_volume_mounts(app_name, assembled_specs):
    volumes = []
    for lib_name in assembled_specs['apps'][app_name].get('depends', {}).get('libs', []):
        lib_spec = assembled_specs['libs'][lib_name]
        lib_repo_path = repo_path(lib_spec['repo'])
        volumes.append("{}:{}".format(lib_repo_path, _container_code_path(lib_spec)))
    return volumes
