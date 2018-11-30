import os

import docker
import logging

from ... import constants
from ...log import log_to_client
from ...memoize import memoized
from ...subprocess import check_output_demoted
from ...compiler.spec_assembler import get_specs

def exec_in_container(container, command, *args):
    client = get_docker_client()
    exec_instance = client.exec_create(container['Id'],
                                       ' '.join([command] + list(args)))
    return client.exec_start(exec_instance['Id'])

def get_dusty_images():
    """Returns all images listed in dusty specs (apps + bundles), in the form repository:tag.  Tag will be set to latest
    if no tag is specified in the specs"""
    specs = get_specs()
    dusty_image_names = [spec['image'] for spec in specs['apps'].values() + specs['services'].values() if 'image' in spec]
    dusty_images = set([name  if ':' in name else "{}:latest".format(name) for name in dusty_image_names])
    return dusty_images

def get_dusty_container_name(service_name):
    return 'dusty_{}_1'.format(service_name)

@memoized
def old_get_docker_env():
    env = {}
    output = check_output_demoted(['docker-machine', 'env', constants.VM_MACHINE_NAME, '--shell', 'bash'], redirect_stderr=True)
    for line in output.splitlines():
        if not line.strip().startswith('export'):
            continue
        k, v = line.strip().split()[1].split('=')
        v = v.replace('"', '')
        env[k] = v
    return env

@memoized
def get_docker_env():
    return {}

@memoized
def get_docker_client():
    return docker.from_env()

@memoized
def old_get_docker_client():
    """Ripped off and slightly modified based on docker-py's
    kwargs_from_env utility function."""
    env = get_docker_env()
    host, cert_path, tls_verify = env['DOCKER_HOST'], env['DOCKER_CERT_PATH'], env['DOCKER_TLS_VERIFY']

    params = {'base_url': host.replace('tcp://', 'https://'),
              'timeout': None,
              'version': 'auto'}
    if tls_verify and cert_path:
        params['tls'] = docker.tls.TLSConfig(
            client_cert=(os.path.join(cert_path, 'cert.pem'),
                         os.path.join(cert_path, 'key.pem')),
            ca_cert=os.path.join(cert_path, 'ca.pem'),
            verify=True,
            ssl_version=None,
            assert_hostname=False)
    return docker.Client(**params)

def get_dusty_containers(services, include_exited=False):
    """Get a list of containers associated with the list
    of services. If no services are provided, attempts to
    return all containers associated with Dusty."""
    client = get_docker_client()
    if services:
        containers = [get_container_for_app_or_service(service, include_exited=include_exited) for service in services]
        return [container for container in containers if container]
    else:
        return [container
                for container in client.containers(all=include_exited)
                if any(name.startswith('/dusty') for name in container.get('Names', []))]

def get_container_for_app_or_service(app_or_service_name, raise_if_not_found=False, include_exited=False):
    client = get_docker_client()
    for container in client.containers(all=include_exited):
        if '/{}'.format(get_dusty_container_name(app_or_service_name)) in container['Names']:
            return container
    if raise_if_not_found:
        raise RuntimeError('No running container found for {}'.format(app_or_service_name))
    return None

def get_canonical_container_name(container):
    """Return the canonical container name, which should be
    of the form dusty_<service_name>_1. Containers are returned
    from the Python client with many names based on the containers
    to which they are linked, but simply taking the shortest name
    should be sufficient to get us the shortest one."""
    return sorted(container['Names'], key=lambda name: len(name))[0][1:]

def get_app_or_service_name_from_container(container):
    return get_canonical_container_name(container).split('_')[1]
