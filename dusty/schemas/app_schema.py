from schemer import Schema, Array

def image_build_isolation_validator():
    def validator(document):
        if 'image' in document and 'build' in document:
            return 'Only one of image and build is allowed in app schema'
        elif 'image' not in document and 'build' not in document:
            return 'Need to have at least one of `image` or `build` in app schema'
    return validator


app_depends_schema = Schema({
    'services': {'type': Array(basestring), 'default': []},
    'apps': {'type': Array(basestring), 'default': []},
    'libs': {'type': Array(basestring), 'default': []}
    })

conditional_links_schema = Schema({
    'services': {'type': Array(basestring), 'default': []},
    'apps': {'type': Array(basestring), 'default': []},
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
    'volumes': {'type': Array(basestring), 'default': []}
    })

app_schema = Schema({
    'repo': {'type': basestring, 'required': True},
    'depends': {'type': app_depends_schema, 'default': {}},
    'conditional_links': {'type': conditional_links_schema, 'default': {}},
    'host_forwarding': {'type': Array(host_forwarding_schema), 'default': []},
    'image': {'type': basestring, 'default': ''},
    'build': {'type': basestring},
    'mount': {'type': basestring, 'default': ''},
    'commands': {'type': commands_schema, 'default': {}},
    'scripts': {'type': Array(script_schema), 'default': []},
    'compose': {'type': dusty_app_compose_schema, 'default': {}}
    }, validates=[image_build_isolation_validator()])
