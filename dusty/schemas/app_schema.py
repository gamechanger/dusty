from schemer import Schema, Array

from .test_schema import test_schema
from .asset_schema import asset_schema

def image_build_isolation_validator():
    def validator(document):
        if 'image' in document and 'build' in document:
            return 'Only one of image and build is allowed in app schema'
        elif 'image' not in document and 'build' not in document:
            return 'Need to have at least one of `image` or `build` in app schema'
    return validator

def repo_mount_validator():
    """If either repo or mount are provided, they must both be provided."""
    def validator(document):
        if 'repo' in document and 'mount' in document:
            return
        elif 'repo' not in document and 'mount' not in document:
            return
        return 'If either `repo` or `mount` are provided, they must both be provided.'
    return validator

app_depends_schema = Schema({
    'services': {'type': Array(basestring), 'default': list},
    'apps': {'type': Array(basestring), 'default': list},
    'libs': {'type': Array(basestring), 'default': list}
    })

conditional_links_schema = Schema({
    'services': {'type': Array(basestring), 'default': list},
    'apps': {'type': Array(basestring), 'default': list},
    })

host_forwarding_schema = Schema({
    'host_name': {'type': basestring},
    'host_port': {'type': int},
    'container_port': {'type': int}
    })

commands_schema = Schema({
    'always': {'type': Array(basestring), 'required': True, 'default': list},
    'once': {'type': Array(basestring), 'default': list}
    })

script_schema = Schema({
    'name': {'type': basestring, 'required': True},
    'description': {'type': basestring},
    'command': {'type': Array(basestring), 'required': True}
    })

dusty_app_compose_schema = Schema({
    'volumes': {'type': Array(basestring), 'default': list}
    }, strict=False)

app_schema = Schema({
    'repo': {'type': basestring, 'default': str},
    'depends': {'type': app_depends_schema, 'default': dict},
    'conditional_links': {'type': conditional_links_schema, 'default': dict},
    'host_forwarding': {'type': Array(host_forwarding_schema), 'default': list},
    'image': {'type': basestring},
    'build': {'type': basestring},
    'mount': {'type': basestring, 'default': str},
    'commands': {'type': commands_schema, 'required': True},
    'scripts': {'type': Array(script_schema), 'default': list},
    'assets': {'type': Array(asset_schema), 'default': list},
    'compose': {'type': dusty_app_compose_schema, 'default': dict},
    'test': {'type': test_schema, 'default': dict}
    }, validates=[
        image_build_isolation_validator(),
        repo_mount_validator(),
    ])
