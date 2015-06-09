from ..compiler.spec_assembler import get_expanded_libs_specs
from ..compiler.compose import get_app_volume_mounts, get_lib_volume_mounts, get_testing_compose_dict
from ..systems.docker.testing_image import ensure_image_exists
from ..systems.docker import get_docker_client
from ..systems.docker.compose import write_composefile, compose_up
from ..systems.rsync import sync_repos_by_app_name, sync_repos_by_lib_name
from ..log import log_to_client

def run_app_or_lib_tests(app_or_lib_name, force_recreate=False):
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
        raise RuntimeError('Argument must be defined app or lib name')

    image_name = "{}_dusty_testing/image".format(app_or_lib_name)
    ensure_image_exists(docker_client, spec['test'], image_name, volumes=volumes, force_recreate=force_recreate)
    _run_tests_with_image(expanded_specs, app_or_lib_name, spec, volumes, image_name)

def _run_tests_with_image(expanded_specs, app_or_lib_name, app_or_lib_spec, app_or_lib_volumes, image_name):
    log_to_client('image name is {}'.format(image_name))
    temporary_compose_config_files = {}
    previous_container_name = None

    for service_name in app_or_lib_spec['test']['services']:
        service_spec = expanded_specs['services'][service_name]
        kwargs = {}
        if previous_container_name is not None:
            kwargs['net_container_identifier'] = previous_container_name
        service_compse_config = get_testing_compose_dict(service_name, service_spec, **kwargs)

        #want to make these temporary files
        compose_file = '/Users/paetling/dusty_testing/service_{}'.format(service_name)
        temporary_compose_config_files[service_name] = compose_file
        write_composefile(service_compse_config, compose_file)

        compose_up(compose_file, service_name)
        #compose only has runs with lower case names
        previous_container_name = "{}_{}_1".format(service_name.lower(), service_name)

    kwargs = {'testing_image_identifier': image_name,
              'volumes': app_or_lib_volumes,
              'command': 'nosetests'} # fix this later

    if previous_container_name is not None:
        kwargs['net_container_identifier'] = previous_container_name
    log_to_client("THE KWARGS FOR GET_TESTING_COMPOSE are {}".format(kwargs))
    compose_file = '/Users/paetling/dusty_testing/service_{}'.format(app_or_lib_name)
    temporary_compose_config_files[app_or_lib_name] = compose_file
    compose_config = get_testing_compose_dict(app_or_lib_name, app_or_lib_spec['test'].get('compose', {}), **kwargs)
    log_to_client(compose_config)
    write_composefile(compose_config, compose_file)
    compose_up(compose_file, app_or_lib_name)

    #need to wait on tests finishing and cleanup shit afterwards


