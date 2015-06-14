from dusty.schemas.base_schema_class import DustySchema
from dusty.schemas.app_schema import app_schema
from dusty.schemas.lib_schema import lib_schema
from dusty.schemas.bundle_schema import bundle_schema

def get_app_dusty_schema(doc):
    if 'image' not in doc and 'build' not in doc:
        doc['image'] = ''
    if 'repo' not in doc:
        doc['repo'] = ''
    return DustySchema(app_schema, doc)

def get_lib_dusty_schema(doc):
    if 'repo' not in doc:
        doc['repo'] = ''
    return DustySchema(lib_schema, doc)

def get_bundle_dusty_schema(doc):
    return DustySchema(bundle_schema, doc)
