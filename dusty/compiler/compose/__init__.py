import logging

import yaml

from ..spec_assembler import get_assembled_specs
from ...path import vm_repo_path
from ... import constants

def get_compose_dict(assembled_specs, port_specs):
    """ This function returns a dictionary representation of a docker-compose.yml file, based on assembled_specs from
    the spec_assembler, and port_specs from the port_spec compiler """
    compose_dict = {}
    for app_name in assembled_specs['apps'].keys():
        compose_dict[app_name] = _composed_app_dict(app_name, assembled_specs, port_specs)
    for service_name in assembled_specs.get('services', []):
        compose_dict[service_name] = _composed_service_dict(service_name, assembled_specs)
    return compose_dict

def _composed_app_dict(app_name, assembled_specs, port_specs):
    """ This function returns a dictionary of the docker-compose.yml specifications for one app """
    logging.info("Compose Compiler: Compiling dict for app {}".format(app_name))
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
    logging.info("Compose Compiler: compiled command {}".format(compose_dict['command']))
    compose_dict['links'] = app_spec.get('depends', {}).get('services', []) + app_spec.get('depends', {}).get('apps', [])
    logging.info("Compose Compiler: links {}".format(compose_dict['links']))
    compose_dict['volumes'] = _get_compose_volumes(app_name, assembled_specs)
    logging.info("Compose Compiler: volumes {}".format(compose_dict['volumes']))
    port_list = _get_ports_list(app_name, port_specs)
    if port_list:
        compose_dict['ports'] = port_list
    logging.info("Compose Compiler: ports {}".format(port_list))
    return compose_dict

def _composed_service_dict(service_name, assembled_specs):
    """This function returns a dictionary of the docker_compose specifications
    for one service. Currently, this is just the Dusty service spec with
    an additional volume mount to support Dusty's cp functionality."""
    compose_dict = assembled_specs['services'][service_name]
    compose_dict.setdefault('volumes', []).append(_get_cp_volume_mount(service_name))
    return compose_dict

def _get_ports_list(app_name, port_specs):
    """ Returns a list of formatted port mappings for an app """
    if app_name not in port_specs['docker_compose']:
        return []
    return ["{}:{}".format(port_spec['mapped_host_port'], port_spec['in_container_port'])
            for port_spec in port_specs['docker_compose'][app_name]]

def _compile_docker_command(app_name, assembled_specs):
    """ This is used to compile the command that will be run when the docker container starts
    up. This command has to install any libs that the app uses, run the `always` command, and
    run the `once` command if the container is being launched for the first time """
    app_spec = assembled_specs['apps'][app_name]
    first_run_file = constants.FIRST_RUN_FILE_PATH
    command = []
    command += _lib_install_commands_for_app(app_name, assembled_specs)
    command.append("cd {}".format(_container_code_path(app_spec)))
    command.append("export PATH=$PATH:{}".format(_container_code_path(app_spec)))
    command.append("if [ ! -f {} ]".format(first_run_file))
    once_command = app_spec['commands'].get("once", "")
    command.append("then mkdir -p {}; touch {}".format(constants.RUN_DIR, first_run_file))
    if once_command:
        command.append(once_command)
    command.append("fi")
    command.append(app_spec['commands']['always'])
    return "sh -c \"{}\"".format('; '.join(command))

def _lib_install_commands_for_app(app_name, assembled_specs):
    """ This returns a list of all the commands that will install libraries for a
    given app """
    libs = assembled_specs['apps'][app_name].get('depends', {}).get('libs', [])
    commands = []
    for lib in libs:
        lib_spec = assembled_specs['libs'][lib]
        install_command = _lib_install_command(lib_spec)
        if install_command:
            commands.append(install_command)
    return commands

def _lib_install_command(lib_spec):
    """ This returns a single commmand that will install a library in a docker container """
    if 'install' not in lib_spec:
        return ''
    return "cd {} && {}".format(lib_spec['mount'], lib_spec['install'])

def _get_compose_volumes(app_name, assembled_specs):
    """ This returns formatted volume specifications for a docker-compose app. We mount the app
    as well as any libs it needs so that local code is used in our container, instead of whatever
    code was in the docker image.

    Additionally, we create a volume for the /cp directory used by Dusty to facilitate
    easy file transfers using `dusty cp`."""
    app_spec = assembled_specs['apps'][app_name]
    volumes = []
    volumes.append(_get_cp_volume_mount(app_name))
    volumes.append(_get_app_volume_mount(app_spec))
    volumes += _get_libs_volume_mounts(app_name, assembled_specs)
    return volumes

def _get_cp_volume_mount(app_name):
    return "{}/{}:{}".format(constants.VM_CP_DIR, app_name, constants.CONTAINER_CP_DIR)

def _get_app_volume_mount(app_spec):
    """ This returns the formatted volume mount spec to mount the local code for an app in the
    container """
    app_repo_path = vm_repo_path(app_spec['repo'])
    return "{}:{}".format(app_repo_path, _container_code_path(app_spec))

def _container_code_path(spec):
    """ Returns the path inside the docker container that a spec (for an app or lib) says it wants
    to live at """
    return spec['mount']

def _get_libs_volume_mounts(app_name, assembled_specs):
    """ Returns a list of the formatted volume mounts for all libs that an app uses """
    volumes = []
    for lib_name in assembled_specs['apps'][app_name].get('depends', {}).get('libs', []):
        lib_spec = assembled_specs['libs'][lib_name]
        lib_repo_path = vm_repo_path(lib_spec['repo'])
        volumes.append("{}:{}".format(lib_repo_path, _container_code_path(lib_spec)))
    return volumes
