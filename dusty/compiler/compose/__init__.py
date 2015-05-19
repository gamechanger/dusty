import yaml
import pprint

from .. import get_assembled_specs
from ...source import repo_path
from ..port_spec import port_spec_document
from ... import constants

def write_compose_file():
    compose_dict = get_compose_dict()
    print pprint.pformat(compose_dict)
    with open("{}/docker-compose.yml".format(constants.COMPOSE_DIR), 'w') as f:
        f.write(yaml.dump(compose_dict, default_flow_style=False, width=10000))
    yield "Written to {}".format("{}/docker-compose.yml".format(constants.COMPOSE_DIR)).encode('utf-8')

def get_compose_dict():
    assembled_specs = get_assembled_specs()
    port_specs = port_spec_document(assembled_specs)
    compose_dict = {}
    for app_name in assembled_specs['apps'].keys():
        compose_dict[app_name] = _composed_app_dict(app_name, assembled_specs, port_specs)
    for service_name in assembled_specs.get('services', []):
        compose_dict[service_name] = _composed_service_dict(service_name, assembled_specs)
    return compose_dict

def _composed_app_dict(app_name, assembled_specs, port_specs):
    app_spec = assembled_specs['apps'][app_name]
    compose_bundle = app_spec.get("compose", {})
    compose_bundle['image'] = app_spec['image']
    compose_bundle['command'] = _compile_docker_command(app_spec)
    compose_bundle['links'] = app_spec.get('depends', {}).get('services', [])
    compose_bundle['volumes'] = _get_compose_volumes(app_name, assembled_specs)
    port_str = _get_ports_list(app_name, port_specs)
    if port_str:
        compose_bundle['ports'] = port_str
    return compose_bundle

def _composed_service_dict(service_name, assembled_specs):
    return assembled_specs['services'][service_name]

def _get_ports_list(app_name, port_specs):
    if app_name not in port_specs['docker_compose']:
        return None
    return ["{}:{}".format(port_specs['docker_compose'][app_name]['mapped_host_port'],
        port_specs['docker_compose'][app_name]['in_container_port'])]

def _compile_docker_command(app_spec):
    first_run_file = constants.FIRST_RUN_FILE
    command = []
    command.append("export PATH=$PATH:{}".format(_container_code_path(app_spec)))
    command.append("if [ ! -f {} ]".format(first_run_file))
    once_command = app_spec['commands'].get("once", "")
    command.append("then touch {}; fi".format(first_run_file))
    if once_command:
        command.append(once_command)
    command.append(app_spec['commands']['always'])
    return "bash -c \"{}\"".format('; '.join(command))

def _get_compose_volumes(app_name, assembled_specs):
    app_spec = assembled_specs['apps'][app_name]
    volumes = []
    volumes.append(_get_app_volume_mount(app_spec))
    volumes += _get_libs_volume_mounts(app_name, assembled_specs)
    return volumes

def _get_app_volume_mount(app_spec):
    app_repo_path = repo_path(app_spec['repo'])
    return "{}:{}".format(app_repo_path, _container_code_path(app_spec))

def _container_code_path(spec):
    return "/gc/{}".format(spec['repo'].split('/')[-1])

def _get_libs_volume_mounts(app_name, assembled_specs):
    volumes = []
    for lib_name in assembled_specs['apps'][app_name].get('depends', {}).get('libs', []):
        lib_spec = assembled_specs['libs'][lib_name]
        lib_repo_path = repo_path(lib_spec['repo'])
        volumes.append("{}:{}".format(lib_repo_path, _container_code_path(lib_spec)))
    return volumes
