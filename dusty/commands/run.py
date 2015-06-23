import os
from subprocess import CalledProcessError

from ..compiler import (compose as compose_compiler, nginx as nginx_compiler,
                        port_spec as port_spec_compiler, spec_assembler)
from ..systems import docker, hosts, nginx, virtualbox, rsync
from ..systems.docker import compose
from ..log import log_to_client
from .repos import update_managed_repos
from .. import constants
from ..command_file import make_up_command_files
from ..source import Repo

def start_local_env(recreate_containers=True, pull_repos=True):
    """This command will use the compilers to get compose specs
    will pass those specs to the systems that need them. Those
    systems will in turn launch the services needed to make the
    local environment go."""
    assembled_spec = spec_assembler.get_assembled_specs()
    if not assembled_spec[constants.CONFIG_BUNDLES_KEY]:
        raise RuntimeError('No bundles are activated. Use `dusty bundles` to activate bundles before running `dusty up`.')

    log_to_client("Ensuring virtualbox vm is running")
    virtualbox.initialize_docker_vm()
    docker_ip = virtualbox.get_docker_vm_ip()

    # Stop will fail if we've never written a Composefile before
    if os.path.exists(constants.COMPOSEFILE_PATH):
        try:
            stop_apps_or_services()
        except CalledProcessError as e:
            log_to_client("WARNING: docker-compose stop failed")
            log_to_client(str(e))
    log_to_client("Compiling together the assembled specs")
    if pull_repos:
        update_managed_repos()
    active_repos = spec_assembler.get_all_repos(active_only=True, include_specs_repo=False)
    log_to_client("Compiling the port specs")
    port_spec = port_spec_compiler.get_port_spec_document(assembled_spec, docker_ip)
    log_to_client("Compiling the nginx config")
    nginx_config = nginx_compiler.get_nginx_configuration_spec(port_spec)
    log_to_client("Creating setup and script bash files")
    make_up_command_files(assembled_spec)
    log_to_client("Compiling docker-compose config")
    compose_config = compose_compiler.get_compose_dict(assembled_spec, port_spec)

    log_to_client("Saving port forwarding to hosts file")
    hosts.update_hosts_file_from_port_spec(port_spec)
    log_to_client("Syncing local repos to the VM")
    rsync.sync_repos(active_repos)
    log_to_client("Saving nginx config and ensure nginx is running")
    nginx.update_nginx_from_config(nginx_config)
    log_to_client("Saving docker-compose config and starting all containers")
    compose.update_running_containers_from_spec(compose_config, recreate_containers=recreate_containers)

    log_to_client("Your local environment is now started!")
    log_to_client("Use `dusty logs` to track your containers")

def stop_apps_or_services(app_or_service_names=None, rm_containers=False):
    """Stop any currently running Docker containers associated with
    Dusty, or associated with the provided apps_or_services. Does not remove
    the service's containers."""
    if app_or_service_names:
        log_to_client("Stopping the following apps or services: {}".format(', '.join(app_or_service_names)))
    else:
        log_to_client("Stopping all running containers associated with Dusty")

    compose.stop_running_services(app_or_service_names)
    if rm_containers:
        compose.rm_containers(app_or_service_names)

def restart_apps_or_services(app_or_service_names=None, sync=True):
    """Restart any containers associated with Dusty, or associated with
    the provided app_or_service_names."""
    if app_or_service_names:
        log_to_client("Restarting the following apps or services: {}".format(', '.join(app_or_service_names)))
    else:
        log_to_client("Restarting all active containers associated with Dusty")

    if sync:
        if app_or_service_names:
            specs = spec_assembler.get_assembled_specs()
            specs_list = [specs['apps'][app_name] for app_name in app_or_service_names if app_name in specs['apps']]
            rsync.sync_repos_by_specs(specs_list)
        else:
            rsync.sync_repos(spec_assembler.get_all_repos(active_only=True, include_specs_repo=False))

    compose.restart_running_services(app_or_service_names)

def restart_apps_by_repo(repo_names, sync=True):
    all_active_repos = spec_assembler.get_all_repos()
    resolved_repos = set([Repo.resolve(all_active_repos, repo_name) for repo_name in repo_names])
    specs = spec_assembler.get_assembled_specs()
    apps_with_repos = set()
    for app_spec in specs['apps'].itervalues():
        if spec_assembler.get_same_container_repos_from_spec(app_spec, specs).intersection(resolved_repos):
            apps_with_repos.add(app_spec.name)
    restart_apps_or_services(list(apps_with_repos), sync=sync)
