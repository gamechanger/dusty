import os
import logging

import yaml

from . import _get_canonical_container_name, get_docker_env, _get_docker_client, _get_dusty_containers
from ... import constants
from ...log import log_to_client
from ...subprocess import check_output_demoted, check_and_log_output_and_error_demoted
from ...compiler.spec_assembler import get_expected_number_of_running_containers
from ...path import parent_dir

def _write_composefile(compose_config, compose_file_location):
    logging.info('Writing new Composefile')
    compose_dir_location = parent_dir(compose_file_location)
    if not os.path.exists(compose_dir_location):
        os.makedirs(compose_dir_location)
    with open(compose_file_location, 'w') as f:
        f.write(yaml.dump(compose_config, default_flow_style=False))

def _compose_up(compose_file_location, project_name, recreate_containers=True):
    logging.info('Running docker-compose up')
    command = ['docker-compose']
    if compose_file_location is not None:
        command += ['-f', compose_file_location]
    if project_name is not None:
        command += ['-p', project_name]
    command += ['up', '-d', '--allow-insecure-ssl']
    if not recreate_containers:
        command.append('--no-recreate')
    # strip_newlines should be True here so that we handle blank lines being caused by `docker pull <image>`
    check_and_log_output_and_error_demoted(command, env=get_docker_env(), strip_newlines=True)

def _compose_stop(compose_file_location, project_name, services):
    logging.info('Running docker-compose stop')
    command = ['docker-compose']
    if compose_file_location is not None:
        command += ['-f', constants.COMPOSEFILE_PATH]
    if project_name is not None:
        command += ['-p', project_name]
    command += ['stop', '-t', '1']
    if services:
        command += services
    check_and_log_output_and_error_demoted(command, env=get_docker_env())

def _compose_restart(services):
    """Well, this is annoying. Compose 1.2 shipped with the
    restart functionality fucking broken, so we can't set a faster
    timeout than 10 seconds (which is way too long) using Compose.
    We are therefore resigned to trying to hack this together
    ourselves. Lame.

    Relevant fix which will make it into the next release:
    https://github.com/docker/compose/pull/1318"""

    def _restart_container(client, container):
        log_to_client('Restarting {}'.format(_get_canonical_container_name(container)))
        client.restart(container['Id'], timeout=1)

    logging.info('Restarting service containers from list: {}'.format(services))
    client = _get_docker_client()
    dusty_containers = _get_dusty_containers(client, services)
    expected_number_of_containers = get_expected_number_of_running_containers() if len(services) == 0 else len(services)
    if len(dusty_containers) != expected_number_of_containers:
        log_to_client("Not going to restart containers. Expected number of containers {} does not match {}".format(expected_number_of_containers, len(dusty_containers)))
        raise RuntimeError("Please use `docker ps -a` to view crashed containers")
    else:
        for container in dusty_containers:
            _restart_container(client, container)

def update_running_containers_from_spec(compose_config, recreate_containers=True):
    """Takes in a Compose spec from the Dusty Compose compiler,
    writes it to the Compose spec folder so Compose can pick it
    up, then does everything needed to make sure boot2docker is
    up and running containers with the updated config."""
    _write_composefile(compose_config, constants.COMPOSEFILE_PATH)
    _compose_up(constants.COMPOSEFILE_PATH, 'dusty', recreate_containers=recreate_containers)

def stop_running_services(services=None):
    """Stop running containers owned by Dusty, or a specific
    list of Compose services if provided.

    Here, "services" refers to the Compose version of the term,
    so any existing running container, by name. This includes Dusty
    apps and services."""
    if services is None:
        services = []
    _compose_stop(constants.COMPOSEFILE_PATH, 'dusty', services)

def restart_running_services(services=None):
    """Restart containers owned by Dusty, or a specific
    list of Compose services if provided.

    Here, "services" refers to the Compose version of the term,
    so any existing running container, by name. This includes Dusty
    apps and services."""
    if services is None:
        services = []
    _compose_restart(services)

