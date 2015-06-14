from __future__ import absolute_import

import docker

from ...compiler.compose import lib_install_commands_for_app_or_lib, container_code_path, get_volume_mounts
from ...log import log_to_client

def _ensure_testing_spec_base_image(docker_client, testing_spec):
    log_to_client('Getting the base image for the new image')
    if 'image' in testing_spec:
        log_to_client('Base image is {}'.format(testing_spec['image']))
        return testing_spec['image']
    elif 'build' in testing_spec:
        image_tag = 'dusty_testing_base/image'
        log_to_client('Need to build the base image based off of the Dockerfile here: {}'.format(testing_spec['build']))
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
    for image in docker_client.images():
        if any(image_name in tag for tag in image['RepoTags']):
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
    container = docker_client.create_container(image=base_image_tag,
                                               command=command,
                                               volumes=create_container_volumes,
                                               host_config=docker.utils.create_host_config(binds=create_container_binds))
    docker_client.start(container=container['Id'])
    docker_client.wait(container=container['Id'])
    new_image = docker_client.commit(container=container['Id'])
    docker_client.tag(image=new_image['Id'], repository=image_name, force=True)

def _spec_for_service(app_or_lib_name, expanded_specs):
    if app_or_lib_name in expanded_specs['apps']:
        return expanded_specs['apps'][app_or_lib_name]
    return expanded_specs['libs'][app_or_lib_name]

def _testing_spec(app_or_lib_name, expanded_specs):
    return _spec_for_service(app_or_lib_name, expanded_specs)['test']

def test_image_name(app_or_lib_name):
    return "dusty/test_{}".format(app_or_lib_name)

def _get_test_image_setup_command(app_or_lib_name, expanded_specs):
    testing_spec = _testing_spec(app_or_lib_name, expanded_specs)
    commands = lib_install_commands_for_app_or_lib(app_or_lib_name, expanded_specs)
    commands += ['cd {}'.format(container_code_path(_spec_for_service(app_or_lib_name, expanded_specs)))]
    commands += [testing_spec['once']]
    return "sh -c \"{}\"".format('; '.join(commands))

def _make_installed_testing_image(docker_client, app_or_lib_name, expanded_specs):
    image_name = test_image_name(app_or_lib_name)
    testing_spec = _testing_spec(app_or_lib_name, expanded_specs)
    base_image_tag = _ensure_testing_spec_base_image(docker_client, testing_spec)
    image_setup_command = _get_test_image_setup_command(app_or_lib_name, expanded_specs)
    volumes = get_volume_mounts(app_or_lib_name, expanded_specs)
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
