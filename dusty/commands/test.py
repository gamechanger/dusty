from ..compiler.spec_assembler import get_expanded_libs_specs
from ..compiler.compose import get_app_volume_mounts, get_lib_volume_mounts
from ..systems.docker.testing_image import ensure_image_exists
from ..systems.docker import get_docker_client
from ..systems.rsync import sync_repos_by_app_name, sync_repos_by_lib_name
from ..log import log_to_client

def test_app_or_lib(app_or_lib_name, force_recreate=False):
    docker_client = get_docker_client()
    expanded_specs = get_expanded_libs_specs()
    if app_or_lib_name in expanded_specs['apps']:
        volumes = get_app_volume_mounts(app_or_lib_name, expanded_specs)
        spec = expanded_specs['apps'][app_or_lib_name]
        sync_repos_by_app_name(expanded_specs, [app_or_lib_name])
    elif app_or_lib_name in expanded_specs['libs']:
        volumes = get_lib_volume_mounts(app_or_lib_name, expanded_specs)
        spec = expanded_specs['libs'][app_or_lib_name]
        sync_repos_by_lib_name(expanded_specs, [app_or_lib_name])
    else:
        raise KeyError('Argument must be app or lib name')
    image_name = "{}_dusty_testing/image".format(app_or_lib_name)
    ensure_image_exists(docker_client, spec['test'], image_name, volumes=volumes, force_recreate=force_recreate)

