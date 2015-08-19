import os
import sys
import textwrap
import time

from prettytable import PrettyTable

from .. import constants
from ..compiler.spec_assembler import (get_expanded_libs_specs, get_specs_repo,
    get_same_container_repos, get_same_container_repos_from_spec)
from ..compiler.compose import get_volume_mounts, get_testing_compose_dict, container_code_path
from ..systems.docker.testing_image import ensure_test_image, test_image_name, ImageCreationError
from ..systems.docker import get_docker_client
from ..systems.docker.compose import write_composefile, compose_up
from ..systems import nfs
from ..systems.virtualbox import initialize_docker_vm
from ..log import log_to_client
from ..command_file import make_test_command_files, dusty_command_file_name
from ..source import Repo
from ..payload import daemon_command

@daemon_command
def test_info_for_app_or_lib(app_or_lib_name):
    expanded_specs = get_expanded_libs_specs()
    spec = expanded_specs.get_app_or_lib(app_or_lib_name)
    if not spec['test']['suites']:
        log_to_client('No test suite registered for {}'.format(app_or_lib_name))
        return

    table = PrettyTable(['Test Suite', 'Description', 'Default Args'])
    for suite_spec in spec['test']['suites']:
        table.add_row([suite_spec['name'],
                       '\n'.join(textwrap.wrap(suite_spec['description'], 80)),
                       suite_spec['default_args']])
    log_to_client(table.get_string(sortby='Test Suite'))

def _update_test_repos(app_or_lib_name):
    specs_repo = get_specs_repo()
    if not specs_repo.is_overridden:
        log_to_client('Updating managed copy of specs-repo before loading specs')
        specs_repo.update_local_repo()
    for repo in get_same_container_repos(app_or_lib_name):
        if not repo.is_overridden:
            repo.update_local_repo()

@daemon_command
def ensure_valid_suite_name(app_or_lib_name, suite_name):
    expanded_specs = get_expanded_libs_specs()
    app_or_lib_spec = expanded_specs.get_app_or_lib(app_or_lib_name)
    found_suite = False
    for suite_spec in app_or_lib_spec['test']['suites']:
        if suite_spec['name'] == suite_name:
            found_suite = True
            break
    if not found_suite:
        raise RuntimeError('Must specify a valid suite name')

@daemon_command
def pull_repos_and_sync(app_or_lib_name, pull_repos=False):
    initialize_docker_vm()
    expanded_specs = get_expanded_libs_specs()
    make_test_command_files(app_or_lib_name, expanded_specs)
    if pull_repos:
        _update_test_repos(app_or_lib_name)
    spec = expanded_specs.get_app_or_lib(app_or_lib_name)
    nfs.update_nfs_with_repos(get_same_container_repos_from_spec(spec))

def run_app_or_lib_tests(app_or_lib_name, suite_name, test_arguments, should_exit=True, force_recreate=False):
    client = get_docker_client()
    expanded_specs = get_expanded_libs_specs()
    spec = expanded_specs.get_app_or_lib(app_or_lib_name)
    test_command = _construct_test_command(spec, suite_name, test_arguments)
    try:
        ensure_test_image(client, app_or_lib_name, expanded_specs, force_recreate=force_recreate)
    except ImageCreationError as e:
        log_to_client('Failed to create test container with error {}'.format(e.code))
        sys.exit(e.code)
    exit_code = _run_tests_with_image(client, expanded_specs, app_or_lib_name, test_command, suite_name)
    if should_exit:
        log_to_client('TESTS {} {}'.format(suite_name, 'FAILED' if exit_code != 0 else 'PASSED'))
        sys.exit(exit_code)
    return exit_code

def run_all_app_or_lib_suites(app_or_lib_name, force_recreate=False):
    expanded_specs = get_expanded_libs_specs()
    spec = expanded_specs.get_app_or_lib(app_or_lib_name)

    summary_table = PrettyTable(['Suite', 'Description', 'Result', 'Time (s)'])
    exit_code = 0

    for index, suite_spec in enumerate(spec['test']['suites']):
        args = [app_or_lib_name, suite_spec['name'], []]
        kwargs = {'should_exit': False, }
        log_to_client('Running test {}'.format(suite_spec['name']))
        if index == 0 and force_recreate:
            log_to_client('Recreating the image during the first test run')
            kwargs['force_recreate'] = True
        start_time = time.time()
        test_result = run_app_or_lib_tests(*args, **kwargs)
        result_str = 'FAIL' if test_result else 'PASS'
        elapsed_time = "{0:.1f}".format(time.time() - start_time)
        summary_table.add_row([suite_spec['name'], suite_spec['description'], result_str, elapsed_time])
        exit_code |= test_result
    log_to_client(summary_table.get_string())
    log_to_client('TESTS {}'.format('FAILED' if exit_code != 0 else 'PASSED'))
    sys.exit(exit_code)

def _construct_test_command(spec, suite_name, test_arguments):
    suite_spec = None
    for suite_dict in spec['test']['suites']:
        if suite_dict['name'] == suite_name:
            suite_spec = suite_dict
            break
    if suite_spec is None:
        raise RuntimeError('{} is not a valid suite name'.format(suite_name))
    if not test_arguments:
        test_arguments = suite_spec['default_args'].split(' ')
    return 'sh {}/{} {}'.format(constants.CONTAINER_COMMAND_FILES_DIR, dusty_command_file_name(spec.name, test_name=suite_name), ' '.join(test_arguments))

def _test_composefile_path(service_name):
    return os.path.expanduser('~/.dusty-testing/test_{}.yml'.format(service_name))

def _compose_project_name(service_name, suite_name):
    # Suite names should be able to have underscores. docker-compose does not allow project name to have underscores
    return 'test{}{}'.format(service_name.lower(), suite_name.lower().replace('_', ''))

def _services_compose_up(expanded_specs, app_or_lib_name, services, suite_name):
    previous_container_names = []
    for service_name in services:
        service_spec = expanded_specs['services'][service_name]
        kwargs = {}
        if previous_container_names:
            kwargs['net_container_identifier'] = previous_container_names[-1]
        service_compose_config = get_testing_compose_dict(service_name, service_spec.plain_dict(), **kwargs)

        composefile_path = _test_composefile_path(service_name)
        write_composefile(service_compose_config, composefile_path)

        compose_up(composefile_path, _compose_project_name(app_or_lib_name, suite_name), quiet=True)
        previous_container_names.append("{}_{}_1".format(_compose_project_name(app_or_lib_name, suite_name), service_name))
    return previous_container_names

def _app_or_lib_compose_up(test_suite_compose_spec, app_or_lib_name, app_or_lib_volumes, test_command, previous_container_name, suite_name):
    image_name = test_image_name(app_or_lib_name)
    kwargs = {'testing_image_identifier': image_name,
              'volumes': app_or_lib_volumes,
              'command': test_command}

    if previous_container_name is not None:
        kwargs['net_container_identifier'] = previous_container_name
    composefile_path = _test_composefile_path(app_or_lib_name)
    compose_config = get_testing_compose_dict(app_or_lib_name, test_suite_compose_spec, **kwargs)
    write_composefile(compose_config, composefile_path)
    compose_up(composefile_path, _compose_project_name(app_or_lib_name, suite_name), quiet=True)
    return '{}_{}_1'.format(_compose_project_name(app_or_lib_name, suite_name), app_or_lib_name)

def _get_suite_spec(testing_spec, suite_name):
    for suite in testing_spec['suites']:
        if suite['name'] == suite_name:
            return suite
    raise RuntimeError('Couldn\'t find suite named {}'.format(suite_name))

def _run_tests_with_image(client, expanded_specs, app_or_lib_name, test_command, suite_name):
    testing_spec = expanded_specs.get_app_or_lib(app_or_lib_name)['test']
    suite_spec = _get_suite_spec(testing_spec, suite_name)

    volumes = get_volume_mounts(app_or_lib_name, expanded_specs, test=True)
    previous_container_names = _services_compose_up(expanded_specs, app_or_lib_name, suite_spec['services'], suite_name)
    previous_container_name = previous_container_names[-1] if previous_container_names else None
    test_container_name = _app_or_lib_compose_up(suite_spec['compose'], app_or_lib_name,
                                                 volumes, test_command, previous_container_name, suite_name)

    for line in client.logs(test_container_name, stdout=True, stderr=True, stream=True):
        log_to_client(line.strip())
    exit_code = client.wait(test_container_name)
    client.remove_container(container=test_container_name, v=True)

    for service_container in previous_container_names:
        log_to_client('Killing service container {}'.format(service_container))
        client.kill(service_container)
        client.remove_container(container=service_container, v=True)
    return exit_code
