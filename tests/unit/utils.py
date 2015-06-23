from dusty.schemas.base_schema_class import DustySchema
from dusty.schemas.app_schema import app_schema
from dusty.schemas.lib_schema import lib_schema
from dusty.schemas.bundle_schema import bundle_schema

def get_app_dusty_schema(doc, name=None):
    if 'image' not in doc and 'build' not in doc:
        doc['image'] = ''
    if 'repo' in doc and 'mount' not in doc:
        doc['mount'] = '/repo'
    if 'mount' in doc and 'repo' not in doc:
        doc['repo'] = '/repo'
    return DustySchema(app_schema, doc, name, 'apps')

def get_lib_dusty_schema(doc, name=None):
    if 'mount' not in doc:
        doc['mount'] = ''
    if 'repo' not in doc:
        doc['repo'] = ''
    return DustySchema(lib_schema, doc, name, 'libs')

def get_bundle_dusty_schema(doc):
    return DustySchema(bundle_schema, doc)

def apply_required_keys(specs):
    for spec_type in ['apps', 'bundles', 'libs', 'services']:
        if spec_type not in specs.keys():
            specs[spec_type] = {}
    for k, v in specs['apps'].iteritems():
        specs['apps'][k] = get_app_dusty_schema(v, k)
    for k, v in specs['libs'].iteritems():
        specs['libs'][k] = get_lib_dusty_schema(v, k)
    return specs
