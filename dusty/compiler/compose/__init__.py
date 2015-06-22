import logging
import copy
import os
import yaml

from ...source import Repo
from ..spec_assembler import get_assembled_specs
from ...path import vm_cp_path
from ... import constants
from ...command_file import dusty_command_file_name
from .common import container_code_path, get_volume_mounts, get_app_volume_mounts, get_lib_volume_mounts

def get_compose_dict(assembled_specs, port_specs):
    """ This function returns a dictionary representation of a docker-compose.yml file, based on assembled_specs from
    the spec_assembler, and port_specs from the port_spec compiler """
    compose_dict = {}
    for app_name in assembled_specs['apps'].keys():
        compose_dict[app_name] = _composed_app_dict(app_name, assembled_specs, port_specs)
    for service_spec in assembled_specs['services'].values():
        compose_dict[service_spec.name] = _composed_service_dict(service_spec)
    return compose_dict

def get_testing_compose_dict(service_name, base_compose_spec, command=None, volumes=None, testing_image_identifier=None, net_container_identifier=None):
    app_compose_dict = copy.deepcopy(base_compose_spec)
    if command is not None:
        app_compose_dict['command'] = command
    if volumes is not None:
        app_compose_dict['volumes'] = volumes
    if net_container_identifier is not None:
        app_compose_dict['net'] = "container:{}".format(net_container_identifier)
    if testing_image_identifier is not None:
        app_compose_dict['image'] = testing_image_identifier
    compose_dict = {service_name: app_compose_dict}
    return compose_dict

def _conditional_links(assembled_specs, app_name):
    """ Given the assembled specs and app_name, this function will return all apps and services specified in
    'conditional_links' if they are specified in 'apps' or 'services' in assembled_specs. That means that
    some other part of the system has declared them as necessary, so they should be linked to this app """
    link_to_apps = []
    potential_links = assembled_specs['apps'][app_name]['conditional_links']
    for potential_link in potential_links['apps']:
        if potential_link in assembled_specs['apps']:
            link_to_apps.append(potential_link)
    for potential_link in potential_links['services']:
        if potential_link in assembled_specs['services']:
            link_to_apps.append(potential_link)
    return link_to_apps

def _get_build_path(app_spec):
    """ Given a spec for an app, returns the value of the `build` field for docker-compose.
    If the path is relative, it is expanded and added to the path of the app's repo. """
    if os.path.isabs(app_spec['build']):
        return app_spec['build']
    return os.path.join(Repo(app_spec['repo']).local_path, app_spec['build'])

def _compile_docker_command(app_spec):
    return 'sh {}/{}'.format(constants.CONTAINER_COMMAND_FILES_DIR, dusty_command_file_name(app_spec.name))

def _composed_app_dict(app_name, assembled_specs, port_specs):
    """ This function returns a dictionary of the docker-compose.yml specifications for one app """
    logging.info("Compose Compiler: Compiling dict for app {}".format(app_name))
    app_spec = assembled_specs['apps'][app_name]
    compose_dict = app_spec["compose"]
    if 'image' in app_spec and 'build' in app_spec:
        raise RuntimeError("image and build are both specified in the spec for {}".format(app_name))
    elif 'image' in app_spec:
        logging.info
        compose_dict['image'] = app_spec['image']
    elif 'build' in app_spec:
        compose_dict['build'] = _get_build_path(app_spec)
    else:
        raise RuntimeError("Neither image nor build was specified in the spec for {}".format(app_name))
    compose_dict['command'] = _compile_docker_command(app_spec)
    logging.info("Compose Compiler: compiled command {}".format(compose_dict['command']))
    compose_dict['links'] = app_spec['depends']['services'] + \
                            app_spec['depends']['apps'] + \
                            _conditional_links(assembled_specs, app_name)
    logging.info("Compose Compiler: links {}".format(compose_dict['links']))
    compose_dict['volumes'] = compose_dict['volumes'] + _get_compose_volumes(app_name, assembled_specs)
    logging.info("Compose Compiler: volumes {}".format(compose_dict['volumes']))
    port_list = _get_ports_list(app_name, port_specs)
    if port_list:
        compose_dict['ports'] = port_list
    logging.info("Compose Compiler: ports {}".format(port_list))
    return compose_dict

def _composed_service_dict(service_spec):
    """This function returns a dictionary of the docker_compose specifications
    for one service. Currently, this is just the Dusty service spec with
    an additional volume mount to support Dusty's cp functionality."""
    compose_dict = service_spec.plain_dict()
    compose_dict.setdefault('volumes', []).append(_get_cp_volume_mount(service_spec.name))
    return compose_dict

def _get_ports_list(app_name, port_specs):
    """ Returns a list of formatted port mappings for an app """
    if app_name not in port_specs['docker_compose']:
        return []
    return ["{}:{}".format(port_spec['mapped_host_port'], port_spec['in_container_port'])
            for port_spec in port_specs['docker_compose'][app_name]]

def _get_compose_volumes(app_name, assembled_specs):
    """ This returns formatted volume specifications for a docker-compose app. We mount the app
    as well as any libs it needs so that local code is used in our container, instead of whatever
    code was in the docker image.

    Additionally, we create a volume for the /cp directory used by Dusty to facilitate
    easy file transfers using `dusty cp`."""
    volumes = []
    volumes.append(_get_cp_volume_mount(app_name))
    volumes += get_app_volume_mounts(app_name, assembled_specs)
    return volumes

def _get_cp_volume_mount(app_name):
    return "{}:{}".format(vm_cp_path(app_name), constants.CONTAINER_CP_DIR)
