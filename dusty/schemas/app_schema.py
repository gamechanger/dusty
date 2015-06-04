from schemer import Schema, Array


app_depends_schema = Schema({
    'services': {'type': Array(basestring)},
    'apps': {'type': Array(basestring)},
    'libs': {'type': Array(basestring)}
    })

conditional_links_schema = Schema({
    'services': {'type': Array(basestring)},
    'apps': {'type': Array(basestring)},
    })

host_forwarding_schema = Schema({
    'host_name': {'type': basestring},
    'host_port': {'type': int},
    'container_port': {'type': int}
    })

commands_schema = Schema({
    'always': {'type': basestring, 'required': True},
    'once': {'type': basestring}
    })

script_schema = Schema({
    'description': {'type': basestring},
    'command': {'type': basestring, 'required': True}
    })

def get_scripts_schema(document):
    scripts_keys = document.keys()
    schema_dict = {key: {'type': script_schema} for key in scripts_keys}
    return Schema(schema_dict)

app_schema = Schema({
    'repo': {'type': basestring, 'required': True},
    'depends': {'type': app_depends_schema},
    'conditional_links': {'type': conditional_links_schema},
    'host_forwarding': {'type': Array(host_forwarding_schema)},
    'image': {'type': basestring},
    'build': {'type': basestring},
    'mount': {'type': basestring},
    'commands': {'type': commands_schema},
    'scripts': {'type': get_scripts_schema},
    'compose': {'type': dict},
    })
