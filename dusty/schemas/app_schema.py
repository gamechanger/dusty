from schemer import Schema, Array

from .test_schema import test_schema

def image_build_isolation_validator():
    def validator(document):
        if 'image' in document and 'build' in document:
            return 'Only one of image and build is allowed in app schema'
        elif 'image' not in document and 'build' not in document:
            return 'Need to have at least one of `image` or `build` in app schema'
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
    'always': {'type': basestring, 'required': True, 'default': ''},
    'once': {'type': basestring, 'default': ''}
    })

script_schema = Schema({
    'name': {'type': basestring, 'required': True},
    'description': {'type': basestring},
    'command': {'type': basestring, 'required': True}
    })

dusty_app_compose_schema = Schema({
    'volumes': {'type': Array(basestring), 'default': list}
    }, strict=False)

app_schema = Schema({
    'repo': {'type': basestring, 'required': True},
    'depends': {'type': app_depends_schema, 'default': dict},
    'conditional_links': {'type': conditional_links_schema, 'default': dict},
    'host_forwarding': {'type': Array(host_forwarding_schema), 'default': list},
    'image': {'type': basestring, 'default': ''},
    'build': {'type': basestring},
    'mount': {'type': basestring, 'default': ''},
    'commands': {'type': commands_schema, 'default': dict},
    'scripts': {'type': Array(script_schema), 'default': list},
    'compose': {'type': dusty_app_compose_schema, 'default': dict},
    'test': {'type': test_schema, 'default': dict}
    }, validates=[image_build_isolation_validator()])
