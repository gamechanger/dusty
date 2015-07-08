from . import exec_in_container, get_docker_client, get_container_for_app_or_service
from ...path import parent_dir

def _create_dir_in_container(client, container, path):
    return exec_in_container(client, container, 'mkdir -p', path)

def _remove_path_in_container(client, container, path):
    return exec_in_container(client, container, 'rm -rf', path)

def _move_in_container(client, container, source_path, dest_path):
    return exec_in_container(client, container, 'mv', source_path, dest_path)

def _recursive_copy_in_container(client, container, source_path, dest_path):
    return exec_in_container(client, container, 'cp -r', source_path, dest_path)

def copy_path_inside_container(app_or_service_name, source_path, dest_path):
    client = get_docker_client()
    container = get_container_for_app_or_service(client, app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(client, container, parent_dir(dest_path))
    _recursive_copy_in_container(client, container, source_path, dest_path)

def move_dir_inside_container(app_or_service_name, source_path, dest_path):
    client = get_docker_client()
    container = get_container_for_app_or_service(client, app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(client, container, parent_dir(dest_path))
    _remove_path_in_container(client, container, dest_path)
    _move_in_container(client, container, '{}/'.format(source_path), dest_path)

def move_file_inside_container(app_or_service_name, source_path, dest_path):
    client = get_docker_client()
    container = get_container_for_app_or_service(client, app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(client, container, parent_dir(dest_path))
    _move_in_container(client, container, source_path, dest_path)
