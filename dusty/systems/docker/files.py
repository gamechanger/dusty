from . import exec_in_container, get_container_for_app_or_service
from ...path import parent_dir

def _create_dir_in_container(container, path):
    return exec_in_container(container, 'mkdir -p', path)

def _remove_path_in_container(container, path):
    return exec_in_container(container, 'rm -rf', path)

def _move_in_container(container, source_path, dest_path):
    return exec_in_container(container, 'mv', source_path, dest_path)

def _recursive_copy_in_container(container, source_path, dest_path):
    return exec_in_container(container, 'cp -r', source_path, dest_path)

def copy_path_inside_container(app_or_service_name, source_path, dest_path):
    container = get_container_for_app_or_service(app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(container, parent_dir(dest_path))
    _recursive_copy_in_container(container, source_path, dest_path)

def move_dir_inside_container(app_or_service_name, source_path, dest_path):
    container = get_container_for_app_or_service(app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(container, parent_dir(dest_path))
    _remove_path_in_container(container, dest_path)
    _move_in_container(container, '{}/'.format(source_path), dest_path)

def move_file_inside_container(app_or_service_name, source_path, dest_path):
    container = get_container_for_app_or_service(app_or_service_name, raise_if_not_found=True)

    _create_dir_in_container(container, parent_dir(dest_path))
    _move_in_container(container, source_path, dest_path)

def container_path_exists(app_or_service_name, path):
    container = get_container_for_app_or_service(app_or_service_name, raise_if_not_found=True)
    return exec_in_container(container, 'sh -c \'[ -e {} ] && echo "yes" || echo "no"\''.format(path)).rstrip() == "yes"
