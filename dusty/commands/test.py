import os
import sys
import textwrap
import time
from contextlib import contextmanager

from prettytable import PrettyTable

from .. import constants
from ..compiler.spec_assembler import (get_expanded_libs_specs, get_specs_repo,
                                       get_same_container_repos, get_same_container_repos_from_spec)
from ..compiler.compose import get_volume_mounts, get_testing_compose_dict, container_code_path
from ..systems.docker.testing_image import test_image_exists, create_test_image, update_test_image, test_image_name, ImageCreationError
from ..systems.docker import get_docker_client
from ..systems.docker.compose import write_composefile, compose_up
from ..systems.docker.config import (get_authed_registries, registry_from_image,
                                     log_in_to_registry)
from ..systems import nfs
from ..systems.virtualbox import initialize_docker_vm
from ..log import log_to_client
from ..command_file import make_test_command_files, dusty_command_file_name
from ..source import Repo
from ..payload import daemon_command
from ..parallel import parallel_task_queue
from ..changeset import RepoChangeSet

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
    with parallel_task_queue() as queue:
        for repo in get_same_container_repos(app_or_lib_name):
            if not repo.is_overridden:
                repo.update_local_repo_async(queue)

def _get_suite_spec(app_or_lib_name, suite_name):
    spec = get_expanded_libs_specs().get_app_or_lib(app_or_lib_name)
    for suite_spec in spec['test']['suites']:
        if suite_spec['name'] == suite_name:
            return suite_spec
    raise RuntimeError('Suite {} not found for {}'.format(suite_name, app_or_lib_name))

@daemon_command
def ensure_valid_suite_name(app_or_lib_name, suite_name):
    _get_suite_spec(app_or_lib_name, suite_name)

@daemon_command
def ensure_vm_initialized():
    log_to_client('Making sure Dusty VM is initialized and running')
    initialize_docker_vm()

def log_in_to_required_registries(app_or_lib_name):
    spec = get_expanded_libs_specs().get_app_or_lib(app_or_lib_name)
    if not spec['test'].get('image') or not spec['test'].get('image_requires_login'):
        return
    registry = registry_from_image(spec['test']['image'])
    if registry not in get_authed_registries():
        log_in_to_registry(registry)

@daemon_command
def setup_for_test(app_or_lib_name, pull_repos=False, force_recreate=False):
    expanded_specs = get_expanded_libs_specs()
    log_to_client('Writing test command files to VM')
    make_test_command_files(app_or_lib_name, expanded_specs)
    if pull_repos:
        _update_test_repos(app_or_lib_name)
    spec = expanded_specs.get_app_or_lib(app_or_lib_name)
    log_to_client('Rigging up NFS mounts for repos under test')
    nfs.update_nfs_with_repos(get_same_container_repos_from_spec(spec))
    ensure_current_image(app_or_lib_name, force_recreate)

def ensure_current_image(app_or_lib_name, force_recreate):
    changeset = RepoChangeSet(constants.CHANGESET_TESTING_KEY, app_or_lib_name)
    if force_recreate or not test_image_exists(app_or_lib_name):
        create_test_image(app_or_lib_name)
        changeset.update()
    elif changeset.has_changed():
        update_test_image(app_or_lib_name)
        changeset.update()

def run_one_suite(app_or_lib_name, suite_name, test_arguments):
    exit_code = _run_tests_with_image(app_or_lib_name, suite_name, test_arguments)

    log_to_client('TESTS {} {}'.format(suite_name, 'FAILED' if exit_code != 0 else 'PASSED'))
    sys.exit(exit_code)

def run_all_suites(app_or_lib_name):
    spec = get_expanded_libs_specs().get_app_or_lib(app_or_lib_name)

    summary_table = PrettyTable(['Suite', 'Description', 'Result', 'Time (s)'])
    exit_code = 0

    for suite_spec in spec['test']['suites']:
        log_to_client('Running test {}'.format(suite_spec['name']))
        start_time = time.time()

        test_result = _run_tests_with_image(app_or_lib_name, suite_spec['name'], None)

        result_str = 'FAIL' if test_result else 'PASS'
        elapsed_time = "{0:.1f}".format(time.time() - start_time)
        summary_table.add_row([suite_spec['name'], suite_spec['description'], result_str, elapsed_time])
        exit_code |= test_result

    log_to_client(summary_table.get_string())
    log_to_client('TESTS {}'.format('FAILED' if exit_code != 0 else 'PASSED'))
    sys.exit(exit_code)

def _construct_test_command(app_or_lib_name, suite_name, test_arguments):
    suite_spec = _get_suite_spec(app_or_lib_name, suite_name)
    if not test_arguments:
        test_arguments = suite_spec['default_args'].split(' ')
    return 'sh {}/{} {}'.format(constants.CONTAINER_COMMAND_FILES_DIR, dusty_command_file_name(app_or_lib_name, test_name=suite_name), ' '.join(test_arguments))

def _test_composefile_path(service_name):
    return os.path.expanduser('~/.dusty-testing/test_{}.yml'.format(service_name))

def _compose_project_name(service_name, suite_name):
    # Suite names should be able to have underscores. docker-compose does not allow project name to have underscores
    return 'test{}{}'.format(service_name.lower(), suite_name.lower().replace('_', ''))

def _test_compose_container_name(compose_project_name, app_or_lib_name):
    return '{}_{}_1'.format(compose_project_name, app_or_lib_name)

def _services_compose_up(expanded_specs, app_or_lib_name, services, suite_name):
    previous_container_names = []
    for service_name in services:
        service_spec = expanded_specs['services'][service_name]
        compose_project_name = _compose_project_name(app_or_lib_name, suite_name)
        container_name = _test_compose_container_name(compose_project_name, service_name)
        kwargs = {'container_name': container_name}
        if previous_container_names:
            kwargs['net_container_identifier'] = previous_container_names[-1]
        service_compose_config = get_testing_compose_dict(service_name, service_spec.plain_dict(), **kwargs)

        composefile_path = _test_composefile_path(service_name)
        write_composefile(service_compose_config, composefile_path)

        compose_up(composefile_path, compose_project_name, quiet=True)
        previous_container_names.append(container_name)
    return previous_container_names

def _app_or_lib_compose_up(test_suite_compose_spec, app_or_lib_name, app_or_lib_volumes, test_command, previous_container_name, suite_name):
    image_name = test_image_name(app_or_lib_name)
    compose_project_name = _compose_project_name(app_or_lib_name, suite_name)
    container_name = _test_compose_container_name(compose_project_name, app_or_lib_name)
    kwargs = {'testing_image_identifier': image_name,
              'volumes': app_or_lib_volumes,
              'command': test_command,
              'container_name': container_name}

    if previous_container_name is not None:
        kwargs['net_container_identifier'] = previous_container_name
    composefile_path = _test_composefile_path(app_or_lib_name)
    compose_config = get_testing_compose_dict(app_or_lib_name, test_suite_compose_spec, **kwargs)
    write_composefile(compose_config, composefile_path)

    compose_up(composefile_path, compose_project_name, quiet=True)
    return container_name

def _cleanup_test_container(client, container_name):
    """
       It is possible that the past test run exited in a bad state.  This will clean it up
    """
    log_to_client('Killing testing container {}'.format(container_name))
    running_containers = client.containers(filters={'name': container_name})
    if running_containers != []:
        client.kill(container_name)

    containers = client.containers(all=True, filters={'name': container_name})
    if containers != []:
        client.remove_container(container_name, v=True)

def _cleanup_containers(app_or_lib_name, suite_name, services):
    compose_project_name = _compose_project_name(app_or_lib_name, suite_name)
    client = get_docker_client()
    for service_name in services:
        service_container_name = _test_compose_container_name(compose_project_name, service_name)
        _cleanup_test_container(client, service_container_name)

    app_container_name = _test_compose_container_name(compose_project_name, app_or_lib_name)
    _cleanup_test_container(client, app_container_name)

@contextmanager
def run_safe_tests(app_or_lib_name, suite_name, services):
    try:
        yield
    #Except needs to be here to catch KeyboardInterrupts
    except:
        raise
    finally:
        _cleanup_containers(app_or_lib_name, suite_name, services)

def _run_tests_with_image(app_or_lib_name, suite_name, test_arguments):
    client = get_docker_client()
    expanded_specs = get_expanded_libs_specs()
    suite_spec = _get_suite_spec(app_or_lib_name, suite_name)
    test_command = _construct_test_command(app_or_lib_name, suite_name, test_arguments)
    volumes = get_volume_mounts(app_or_lib_name, expanded_specs, test=True)

    with run_safe_tests(app_or_lib_name, suite_name, suite_spec['services']):
        previous_container_names = _services_compose_up(expanded_specs, app_or_lib_name, suite_spec['services'], suite_name)
        previous_container_name = previous_container_names[-1] if previous_container_names else None
        test_container_name = _app_or_lib_compose_up(suite_spec['compose'], app_or_lib_name,
                                                     volumes, test_command, previous_container_name, suite_name)

        for line in client.logs(test_container_name, stdout=True, stderr=True, stream=True):
            log_to_client(line.strip())
        exit_code = client.wait(test_container_name)

    return exit_code
