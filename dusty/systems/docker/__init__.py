import os

import docker
import logging

from ...log import log_to_client
from ...demote import check_output_demoted
from ...compiler.spec_assembler import get_specs
from ...path import parent_dir


def _exec_in_container(client, container, command, *args):
    exec_instance = client.exec_create(container['Id'],
                                       ' '.join([command] + list(args)))
    return client.exec_start(exec_instance['Id'])

def _create_dir_in_container(client, container, path):
    return _exec_in_container(client, container, 'mkdir -p', path)

def _remove_path_in_container(client, container, path):
    return _exec_in_container(client, container, 'rm -rf', path)

def _move_in_container(client, container, source_path, dest_path):
    return _exec_in_container(client, container, 'mv', source_path, dest_path)

def _recursive_copy_in_container(client, container, source_path, dest_path):
    return _exec_in_container(client, container, 'cp -r', source_path, dest_path)

def copy_path_inside_container(app_or_service_name, source_path, dest_path):
    client = _get_docker_client()
    container = _get_container_for_app_or_service(client, app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(client, container, parent_dir(dest_path))
    _recursive_copy_in_container(client, container, source_path, dest_path)

def move_dir_inside_container(app_or_service_name, source_path, dest_path):
    client = _get_docker_client()
    container = _get_container_for_app_or_service(client, app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(client, container, parent_dir(dest_path))
    _remove_path_in_container(client, container, dest_path)
    _move_in_container(client, container, '{}/'.format(source_path), dest_path)

def move_file_inside_container(app_or_service_name, source_path, dest_path):
    client = _get_docker_client()
    container = _get_container_for_app_or_service(client, app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(client, container, parent_dir(dest_path))
    _move_in_container(client, container, source_path, dest_path)

def get_dusty_images():
    """Returns all images listed in dusty specs (apps + bundles), in the form repository:tag.  Tag will be set to latest
    if no tag is specified in the specs"""
    specs = get_specs()
    dusty_image_names = [spec['image'] for spec in specs.get('apps', {}).values() + specs.get('services', {}).values() if 'image' in spec]
    dusty_images = set([name  if ':' in name else "{}:latest".format(name) for name in dusty_image_names])
    return dusty_images

def get_dusty_container_name(service_name):
    return 'dusty_{}_1'.format(service_name)

def _get_docker_env():
    output = check_output_demoted(['boot2docker', 'shellinit'])
    env = {}
    for line in output.splitlines():
        k, v = line.strip().split()[1].split('=')
        env[k] = v
    return env

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

def _get_dusty_containers(client, services, include_exited=False):
    """Get a list of containers associated with the list
    of services. If no services are provided, attempts to
    return all containers associated with Dusty."""
    if services:
        return [container
                for container in client.containers(all=include_exited)
                if any('/{}'.format(get_dusty_container_name(service)) in container.get('Names', [])
                       for service in services)]
    else:
        return [container
                for container in client.containers(all=include_exited)
                if any(name.startswith('/dusty') for name in container.get('Names', []))]

def _get_container_for_app_or_service(client, app_or_service_name, raise_if_not_found=False):
    for container in client.containers():
        if '/{}'.format(get_dusty_container_name(app_or_service_name)) in container['Names']:
            return container
    if raise_if_not_found:
        raise RuntimeError('No running container found for {}'.format(app_or_service_name))

def _get_canonical_container_name(container):
    """Return the canonical container name, which should be
    of the form dusty_<service_name>_1. Containers are returned
    from the Python client with many names based on the containers
    to which they are linked, but simply taking the shortest name
    should be sufficient to get us the shortest one."""
    return sorted(container['Names'], key=lambda name: len(name))[0][1:]

def get_dusty_containers(app_or_service_names):
    client = _get_docker_client()
    return _get_dusty_containers(client, app_or_service_names)
