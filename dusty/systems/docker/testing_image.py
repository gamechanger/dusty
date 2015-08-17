from __future__ import absolute_import
import logging
import docker

from ...compiler.compose import container_code_path, get_volume_mounts
from ...log import log_to_client
from ...command_file import dusty_command_file_name, lib_install_commands_for_app_or_lib
from .common import spec_for_service
from ... import constants

def _ensure_testing_spec_base_image(docker_client, testing_spec):
    log_to_client('Getting the base image for the new image')
    if 'image' in testing_spec:
        log_to_client('Base image is {}'.format(testing_spec['image']))
        return testing_spec['image']
    elif 'build' in testing_spec:
        image_tag = 'dusty_testing_base/image'
        log_to_client('Need to build the base image based off of the Dockerfile here: {}'.format(testing_spec['build']))
        try:
            docker_client.remove_image(image=image_tag)
        except:
            logging.info('Not able to remove image {}'.format(image_tag))
        docker_client.build(path=testing_spec['build'], tag=image_tag)
        return image_tag

def _get_split_volumes(volumes):
    split_volumes = []
    for volume in volumes:
        volume_list = volume.split(':')
        split_volumes.append({'host_location': volume_list[0],
                              'container_location': volume_list[1]})
    return split_volumes

def _get_create_container_volumes(split_volumes):
    return [volume_dict['container_location'] for volume_dict in split_volumes]

def _get_create_container_binds(split_volumes):
    binds_dict = {}
    for volume_dict in split_volumes:
        binds_dict[volume_dict['host_location']] =  {'bind': volume_dict['container_location'], 'ro': False}
    return binds_dict

def _ensure_image_exists(docker_client, image_name):
    full_image_name = image_name
    if ':' not in image_name:
        full_image_name = '{}:latest'.format(image_name)
    for image in docker_client.images():
        if full_image_name in image['RepoTags']:
            break
    else:
        split = image_name.split(':')
        repo, tag = split[0], 'latest' if len(split) == 1 else split[1]
        docker_client.pull(repo, tag, insecure_registry=True)

def _make_installed_requirements_image(docker_client, base_image_tag, command, image_name, volumes):
    split_volumes = _get_split_volumes(volumes)
    create_container_volumes = _get_create_container_volumes(split_volumes)
    create_container_binds = _get_create_container_binds(split_volumes)

    _ensure_image_exists(docker_client, base_image_tag)
    try:
        docker_client.remove_image(image=image_name)
    except:
        logging.info('Not able to remove image {}'.format(image_name))
    container = docker_client.create_container(image=base_image_tag,
                                               command=command,
                                               volumes=create_container_volumes,
                                               host_config=docker.utils.create_host_config(binds=create_container_binds))
    docker_client.start(container=container['Id'])
    log_to_client('Running commands to create new image:')
    for line in docker_client.logs(container['Id'], stdout=True, stderr=True, stream=True):
        log_to_client(line.strip())
    new_image = docker_client.commit(container=container['Id'])
    docker_client.tag(image=new_image['Id'], repository=image_name, force=True)

def _testing_spec(app_or_lib_name, expanded_specs):
    return spec_for_service(app_or_lib_name, expanded_specs)['test']

def test_image_name(app_or_lib_name):
    return "dusty/test_{}".format(app_or_lib_name)

def _get_test_image_setup_command(app_or_lib_name, app_or_lib_spec):
    return 'sh {}/{}'.format(constants.CONTAINER_COMMAND_FILES_DIR, dusty_command_file_name(app_or_lib_name))

def _make_installed_testing_image(docker_client, app_or_lib_name, expanded_specs):
    image_name = test_image_name(app_or_lib_name)
    testing_spec = _testing_spec(app_or_lib_name, expanded_specs)
    base_image_tag = _ensure_testing_spec_base_image(docker_client, testing_spec)
    image_setup_command = _get_test_image_setup_command(app_or_lib_name, spec_for_service(app_or_lib_name, expanded_specs))
    volumes = get_volume_mounts(app_or_lib_name, expanded_specs, test=True)
    _make_installed_requirements_image(docker_client, base_image_tag, image_setup_command, image_name, volumes)

def ensure_test_image(docker_client, app_or_lib_name, expanded_specs, force_recreate=False):
    volumes = get_volume_mounts(app_or_lib_name, expanded_specs)
    images = docker_client.images()
    image_name = test_image_name(app_or_lib_name)
    image_exists = False
    for image in images:
        if any(image_name in tag for tag in image['RepoTags']):
            image_exists = True
            break
    if force_recreate or not image_exists:
        log_to_client('Creating a new image named {}, with installed dependencies for the app or lib'.format(image_name))
        _make_installed_testing_image(docker_client, app_or_lib_name, expanded_specs)
        log_to_client('Image is now created')
