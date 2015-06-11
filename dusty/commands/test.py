import os

from .. import constants
from ..compiler.spec_assembler import get_expanded_libs_specs
from ..compiler.compose import get_app_volume_mounts, get_lib_volume_mounts, get_testing_compose_dict
from ..systems.docker.testing_image import ensure_image_exists
from ..systems.docker import get_docker_client
from ..systems.docker.compose import write_composefile, compose_up
from ..systems.rsync import sync_repos_by_app_name, sync_repos_by_lib_name
from ..log import log_to_client

def run_app_or_lib_tests(app_or_lib_name, suite_name, test_arguments, force_recreate=False):
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

    test_command = _construct_test_command(spec, suite_name, test_arguments)
    image_name = "{}_dusty_testing/image".format(app_or_lib_name)
    ensure_image_exists(docker_client, spec['test'], image_name, volumes=volumes, force_recreate=force_recreate)
    _run_tests_with_image(expanded_specs, app_or_lib_name, spec, volumes, image_name, test_command)

def _construct_test_command(spec, suite_name, test_arguments):
    suite_command = None
    for suite_dict in spec['test']['suites']:
        if suite_dict['name'] == suite_name:
            suite_command = suite_dict['command']
            break
    if suite_command is None:
        raise RuntimeError('{} is not a valid suite name'.format(suite_name))
    test_command = '{} {}'.format(suite_command, ' '.join(test_arguments))
    log_to_client('Command to run in test is {}'.format(test_command))
    return test_command

def _test_composefile_path(service_name):
    return os.path.expanduser('~/.dusty-testing/test_{}.yml'.format(service_name))

def _services_compose_up(expanded_specs, app_or_lib_spec):
    previous_container_names = []
    for service_name in app_or_lib_spec['test']['services']:
        service_spec = expanded_specs['services'][service_name]
        kwargs = {}
        if previous_container_names:
            kwargs['net_container_identifier'] = previous_container_names[-1]
        service_compose_config = get_testing_compose_dict(service_name, service_spec, **kwargs)

        #want to make these temporary files
        composefile_path = _test_composefile_path(service_name)
        write_composefile(service_compose_config, composefile_path)
        log_to_client('Compose config {}: \n {}'.format(service_name, service_compose_config))

        compose_up(composefile_path, service_name)
        #compose only has runs with lower case names
        previous_container_names.append("{}_{}_1".format(service_name.lower(), service_name))
    return previous_container_names

def _app_or_lib_compose_up(app_or_lib_spec, app_or_lib_name, image_name,
                           app_or_lib_volumes, test_command, previous_container_name):
    kwargs = {'testing_image_identifier': image_name,
              'volumes': app_or_lib_volumes,
              'command': test_command}

    if previous_container_name is not None:
        kwargs['net_container_identifier'] = previous_container_name
    composefile_path = _test_composefile_path(app_or_lib_name)
    compose_config = get_testing_compose_dict(app_or_lib_name, app_or_lib_spec['test'].get('compose', {}), **kwargs)
    write_composefile(compose_config, composefile_path)
    compose_up(composefile_path, app_or_lib_name)
    log_to_client('Compose config {}: \n {}'.format(app_or_lib_name, compose_config))

def _run_tests_with_image(expanded_specs, app_or_lib_name, app_or_lib_spec, app_or_lib_volumes, image_name, test_command):
    log_to_client('image name is {}'.format(image_name))

    previous_container_names = _services_compose_up(expanded_specs, app_or_lib_spec)
    previous_container_name = previous_container_names[-1] if previous_container_names else None
    _app_or_lib_compose_up(app_or_lib_spec, app_or_lib_name, image_name,
                           app_or_lib_volumes, test_command, previous_container_name)
