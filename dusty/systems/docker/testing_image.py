from __future__ import absolute_import
import docker

from ...compiler.compose import container_code_path, get_volume_mounts
from ...compiler.spec_assembler import get_expanded_libs_specs
from ...log import log_to_client
from ...command_file import dusty_command_file_name, lib_install_commands_for_app_or_lib
from .common import spec_for_service
from . import get_docker_client
from ... import constants

class ImageCreationError(Exception):
    def __init__(self, code):
        self.code = code
        message = 'Run exited with code {}'.format(code)
        super(ImageCreationError, self).__init__(message)

def _ensure_base_image(app_or_lib_name):
    testing_spec = _testing_spec(app_or_lib_name)
    log_to_client('Getting the base image for the new image')
    docker_client = get_docker_client()
    if 'image' in testing_spec:
        _ensure_image_pulled(testing_spec['image'])
        return testing_spec['image']
    elif 'build' in testing_spec:
        image_tag = 'dusty_testing_base/image'
        log_to_client('Need to build the base image based off of the Dockerfile here: {}'.format(testing_spec['build']))
        try:
            docker_client.remove_image(image=image_tag)
        except:
            log_to_client('Not able to remove image {}'.format(image_tag))
        docker_client.build(path=testing_spec['build'], tag=image_tag)
        return image_tag

def _ensure_image_pulled(image_name):
    docker_client = get_docker_client()
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

def _get_split_volumes(volumes):
    print volumes
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

def _create_tagged_image(base_image_tag, new_image_tag, app_or_lib_name):
    docker_client = get_docker_client()

    command = _get_test_image_setup_command(app_or_lib_name)
    split_volumes = _get_split_volumes(get_volume_mounts(app_or_lib_name, get_expanded_libs_specs(), test=True))
    create_container_volumes = _get_create_container_volumes(split_volumes)
    create_container_binds = _get_create_container_binds(split_volumes)

    container = docker_client.create_container(image=base_image_tag,
                                               command=command,
                                               volumes=create_container_volumes,
                                               host_config=docker.utils.create_host_config(binds=create_container_binds))
    docker_client.start(container=container['Id'])
    log_to_client('Running commands to create new image:')
    for line in docker_client.logs(container['Id'], stdout=True, stderr=True, stream=True):
        log_to_client(line.strip())
    exit_code = docker_client.wait(container['Id'])
    if exit_code:
        raise ImageCreationError(exit_code)

    new_image = docker_client.commit(container=container['Id'])
    try:
        docker_client.remove_image(image=new_image_tag)
    except:
        log_to_client('Not able to remove image {}'.format(new_image_tag))
    docker_client.tag(image=new_image['Id'], repository=new_image_tag, force=True)
    docker_client.remove_container(container=container['Id'], v=True)

def _testing_spec(app_or_lib_name):
    expanded_specs = get_expanded_libs_specs()
    return spec_for_service(app_or_lib_name, expanded_specs)['test']

def test_image_name(app_or_lib_name):
    return "dusty/test_{}".format(app_or_lib_name)

def _get_test_image_setup_command(app_or_lib_name):
    return 'sh {}/{}'.format(constants.CONTAINER_COMMAND_FILES_DIR, dusty_command_file_name(app_or_lib_name))

def test_image_exists(app_or_lib_name):
    image_name = test_image_name(app_or_lib_name)
    docker_client = get_docker_client()
    images = docker_client.images()
    return any((image_name in image['RepoTags'] or '{}:latest'.format(image_name) in image['RepoTags'])
               for image in images)

def create_test_image(app_or_lib_name):
    """
    Create a new test image by applying changes to the base image specified
    in the app or lib spec
    """
    log_to_client('Creating the testing image')
    base_image_tag = _ensure_base_image(app_or_lib_name)
    new_image_name = test_image_name(app_or_lib_name)
    _create_tagged_image(base_image_tag, new_image_name, app_or_lib_name)

def update_test_image(app_or_lib_name):
    """
    Apply updates to an existing testing image that has already been created
    by Dusty - updating this test image should be quicker than creating a new
    test image from the base image in the spec
    """
    log_to_client('Updating the testing image')
    if not test_image_exists(app_or_lib_name):
        create_test_image(app_or_lib_name)
        return
    test_image_tag = test_image_name(app_or_lib_name)
    _create_tagged_image(test_image_tag, test_image_tag, app_or_lib_name)
