import os
import logging
from copy import copy
import re

import yaml
import docker

from ... import constants
from ...log import log_to_client
from ...config import get_config_value, assert_config_key
from ...demote import check_output_demoted, check_and_log_output_and_error_demoted
from ...compiler.spec_assembler import get_expected_number_of_running_containers, get_specs

def _get_docker_client():
    """Ripped off and slightly modified based on docker-py's
    kwargs_from_env utility function."""
    env = _get_docker_env()
    host, cert_path, tls_verify = env['DOCKER_HOST'], env['DOCKER_CERT_PATH'], env['DOCKER_TLS_VERIFY']

    params = {'base_url': host.replace('tcp://', 'https://')}
    if tls_verify and cert_path:
        params['tls'] = docker.tls.TLSConfig(
            client_cert=(os.path.join(cert_path, 'cert.pem'),
                         os.path.join(cert_path, 'key.pem')),
            ca_cert=os.path.join(cert_path, 'ca.pem'),
            verify=True,
            ssl_version=None,
            assert_hostname=False)
    return docker.Client(**params)

def _get_docker_env():
    output = check_output_demoted(['boot2docker', 'shellinit'])
    env = {}
    for line in output.splitlines():
        k, v = line.strip().split()[1].split('=')
        env[k] = v
    return env

def _composefile_path():
    return os.path.join(constants.COMPOSE_DIR, 'docker-compose.yml')

def _write_composefile(compose_config):
    logging.info('Writing new Composefile')
    if not os.path.exists(constants.COMPOSE_DIR):
        os.makedirs(constants.COMPOSE_DIR)
    with open(_composefile_path(), 'w') as f:
        f.write(yaml.dump(compose_config, default_flow_style=False))

def _compose_up():
    logging.info('Running docker-compose up')
    check_and_log_output_and_error_demoted(['docker-compose', '-f', _composefile_path(), '-p', 'dusty',
                                            'up', '-d', '--allow-insecure-ssl'],
                                           env=_get_docker_env())

def _compose_stop(services):
    logging.info('Running docker-compose stop')
    command = ['docker-compose', '-f', _composefile_path(),
               '-p', 'dusty', 'stop', '-t', '1']
    if services:
        command += services
    check_and_log_output_and_error_demoted(command, env=_get_docker_env())

def _get_dusty_containers(client, services, include_exited=False):
    """Get a list of containers associated with the list
    of services. If no services are provided, attempts to
    return all containers associated with Dusty."""
    if services:
        return [container
                for container in client.containers(all=include_exited)
                if any('/dusty_{}_1'.format(service) in container.get('Names', [])
                       for service in services)]
    else:
        return [container
                for container in client.containers(all=include_exited)
                if any(name.startswith('/dusty') for name in container.get('Names', []))]

def _get_canonical_container_name(container):
    """Return the canonical container name, which should be
    of the form dusty_<service_name>_1. Containers are returned
    from the Python client with many names based on the containers
    to which they are linked, but simply taking the shortest name
    should be sufficient to get us the shortest one."""
    return sorted(container['Names'], key=lambda name: len(name))[0][1:]

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

def update_running_containers_from_spec(compose_config):
    """Takes in a Compose spec from the Dusty Compose compiler,
    writes it to the Compose spec folder so Compose can pick it
    up, then does everything needed to make sure boot2docker is
    up and running containers with the updated config."""
    assert_config_key('mac_username')
    _write_composefile(compose_config)
    _compose_up()

def stop_running_services(services=None):
    """Stop running containers owned by Dusty, or a specific
    list of Compose services if provided.

    Here, "services" refers to the Compose version of the term,
    so any existing running container, by name. This includes Dusty
    apps and services."""
    if services is None:
        services = []
    _compose_stop(services)

def restart_running_services(services=None):
    """Restart containers owned by Dusty, or a specific
    list of Compose services if provided.

    Here, "services" refers to the Compose version of the term,
    so any existing running container, by name. This includes Dusty
    apps and services."""
    if services is None:
        services = []
    _compose_restart(services)

def get_dusty_containers(app_or_service_names):
    client = _get_docker_client()
    return _get_dusty_containers(client, app_or_service_names)

def _get_exited_dusty_containers(client):
    all_containers = _get_dusty_containers(client, None, include_exited=True)
    stopped_containers = []
    for container in all_containers:
        if 'Exited' in container['Status']:
            stopped_containers.append(container)
    return stopped_containers

def remove_exited_dusty_containers():
    """Removed all dusty containers with 'Exited' in their status"""
    client = _get_docker_client()
    exited_containers = _get_exited_dusty_containers(client)
    removed_containers = []
    for container in exited_containers:
        log_to_client("Removing container {}".format(container['Names'][0]))
        try:
            client.remove_container(container['Id'])
            removed_containers.append(container)
        except Exception as e:
            log_to_client(e.message or str(e))
    return removed_containers

def _remove_dangling_images(client):
    dangling_images = client.images(all=True, filters={'dangling': True})
    removed = []
    for image in dangling_images:
        try:
            client.remove_image(image['Id'])
        except Exception as e:
            logging.info("Couldn't remove image {}".format(image['RepoTags']))
        else:
            log_to_client("Removed Image {}".format(image['RepoTags']))
            removed.append(image)
    return removed

def get_dusty_images():
    """Returns all images listed in dusty specs (apps + bundles), in the form repository:tag.  Tag will be set to latest
    if no tag is specified in the specs"""
    specs = get_specs()
    dusty_image_names = [spec['image'] for spec in specs.get('apps', {}).values() + specs.get('services', {}).values() if 'image' in spec]
    dusty_images = set([name  if ':' in name else "{}:latest".format(name) for name in dusty_image_names])
    return dusty_images

def remove_images():
    """Removes all dangling images as well as all images referenced in a dusty spec; forceful removal is not used"""
    client = _get_docker_client()
    removed = _remove_dangling_images(client)
    dusty_images = get_dusty_images()
    all_images = client.images(all=True)
    for image in all_images:
        if image['RepoTags'][0] in dusty_images:
            try:
                client.remove_image(image['Id'])
            except Exception as e:
                logging.info("Couldn't remove image {}".format(image['RepoTags']))
            else:
                log_to_client("Removed Image {}".format(image['RepoTags']))
                removed.append(image)
    return removed
