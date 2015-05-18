import yaml

from .. import get_assembled_specs
from ...source import repo_path
from ..port_spec import port_spec_document
from ... import constants

def write_compose_file():
    compose_dict = get_compose_dict()
    with open(constants.COMPOSE_YML_PATH, 'w') as f:
        f.write(yaml.dump(compose_dict))
    return "Written to {}".format(constants.COMPOSE_YML_PATH)

def get_compose_dict():
    assembled_specs = get_assembled_specs()
    port_specs = port_spec_document(assembled_specs)
    compose_dict = {}
    for app_name in assembled_specs['bundles'].keys():
        compose_dict[bundle_name] = _composed_app_dict(app_name, assembled_specs, port_specs)
    for service_name in assembled_specs.get('services', []):
        compose_dict[service_name] = _composed_service_dict(service_name, assembled_specs)
    return compose_dict

def _composed_app_dict(app_name, assembled_specs, port_specs):
    app_spec = assembled_specs['apps'][app_name]
    compose_bundle = app_spec.get("compose", {})
    compose_bundle['build'] = "{}/{}".format(repo_path(app_spec['repo']), app_spec.get('build', "."))
    compose_bundle['command'] = _compile_docker_command(app_spec)
    compose_bundle['links'] = app_spec.get('depends', {}).get('services', [])
    compose_bundle['ports'] = _get_ports_list(app_name, port_specs)

def _composed_service_dict(service_name, assembled_specs):
    return assembled_specs['services'][service_name]

def _get_ports_list(app_name, port_specs):
    return ["{}:{}".format(port_specs['docker_compose'][app_name]['mapped_host_port'],
        port_specs['docker_compose'][app_name]['in_container_port'])]

def _compile_docker_command(app_spec):
    first_run_file = constants.FIRST_RUN_FILEpla
    command = []
    command.append("if [ ! -f {} ]; then".format(first_run_file))
    command.append(app_spec['commands'].get("once", ""))
    command.append("\ttouch {}; fi".format(first_run_file))
    command.append(app_spec['commands']['always'])
    return "bash -c \"{}\"".format('; '.join(command))
