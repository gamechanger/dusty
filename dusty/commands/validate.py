from copy import copy
import logging

from schemer import ValidationException

from ..compiler.spec_assembler import get_specs_path, get_specs_from_path
from ..log import log_to_client
from ..schemas import app_schema, bundle_schema, lib_schema

def _check_bare_minimum(specs):
    if not specs.get('bundles') or not specs.get('apps'):
        log_to_client("WARNING: You'll need at least one bundle referencing one app for Dusty to work")

def _ensure_app_build_or_image(app):
    if 'image' in app and 'build' in app:
        raise ValidationException("Keys `image` and `build` are mutually exclusive")
    elif 'image' not in app and 'build' not in app:
        raise ValidationException("Each app must contain either an `image` or a `build` field")

def _validate_fields_with_schemer(specs):
    for app in specs.get('apps', []).values():
        app_schema.validate(app)
        _ensure_app_build_or_image(app)
    for bundle in specs.get('bundles', []).values():
        bundle_schema.validate(bundle)
    for lib in specs.get('libs', []).values():
        lib_schema.validate(lib)

def _validate_app_references(app, specs):
    for spec_type in ['apps', 'libs', 'services']:
        dependent = app.get('depends', {}).get(spec_type, []) + app.get('conditional_links', {}).get(spec_type, [])
        assert(all(spec_name in specs.get(spec_type, {}).keys() for spec_name in dependent))

def _validate_bundle_references(bundle, specs):
    for app in bundle['apps']:
        assert(app in specs['apps'].keys())

def _validate_lib_references(lib, specs):
    for lib in lib.get('depends', {}).get('libs', []):
        assert(lib in specs['libs'].keys())

def _validate_spec_names(specs):
    for app in specs.get('apps', {}).values():
        _validate_app_references(app, specs)
    for bundle in specs.get('bundles', {}).values():
        _validate_bundle_references(bundle, specs)
    for lib in specs.get('libs', {}).values():
        _validate_lib_references(lib, specs)

def _cycle_check(spec_type, name, specs, upstream):
    for dependent in specs[spec_type][name].get('depends', {}).get(spec_type, []):
        if dependent in upstream:
            raise ValidationException("Cycle found for {0} {1}.  Upstream {0}: {2}".format(spec_type, name, upstream))
        else:
            new_upstream = copy(upstream)
            new_upstream.add(dependent)
            _cycle_check(spec_type, dependent, specs, new_upstream)

def _validate_cycle_free(specs):
    for spec_type in ['apps', 'libs']:
        for name in specs.get(spec_type, {}).keys():
            _cycle_check(spec_type, name, specs, set([name]))

def validate_specs_from_path(specs_path):
    log_to_client("Validating specs at path {}".format(specs_path))
    specs = get_specs_from_path(specs_path)
    _check_bare_minimum(specs)
    _validate_fields_with_schemer(specs)
    _validate_spec_names(specs)
    _validate_cycle_free(specs)
    log_to_client("Validation Complete!")

def validate_specs():
    validate_specs_from_path(get_specs_path())
