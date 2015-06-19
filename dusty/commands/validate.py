from copy import copy
import logging
import os

from schemer import ValidationException

from ..compiler.spec_assembler import get_specs_path, get_specs_from_path
from ..log import log_to_client
from ..schemas import app_schema, bundle_schema, lib_schema
from ..schemas.base_schema_class import notifies_validation_exception
from .. import constants

def _check_bare_minimum(specs):
    if not specs.get('bundles'):
        raise ValidationException("No Bundles found - exiting")

def _validate_app_references(app, specs):
    for spec_type in ['apps', 'libs', 'services']:
        dependent = app['depends'][spec_type]
        if spec_type in ['apps', 'services']:
            dependent += app['conditional_links'][spec_type]
        assert(all(spec_name in specs[spec_type].keys() for spec_name in dependent))

def _validate_bundle_references(bundle, specs):
    for app in bundle['apps']:
        assert(app in specs['apps'].keys())

def _validate_lib_references(lib, specs):
    for lib in lib['depends']['libs']:
        assert(lib in specs['libs'].keys())

def _validate_spec_names(specs):
    for app in specs['apps'].values():
        _validate_app_references(app, specs)
    for bundle in specs['bundles'].values():
        _validate_bundle_references(bundle, specs)
    for lib in specs['libs'].values():
        _validate_lib_references(lib, specs)

def _cycle_check(spec, specs, upstream):
    for dependent in spec['depends'][spec.spec_type]:
        print dependent
        if dependent in upstream:
            raise ValidationException("Cycle found for {0} {1}.  Upstream {0}: {2}".format(spec.spec_type, spec.name, upstream))
        else:
            new_upstream = copy(upstream)
            new_upstream.add(dependent)
            _cycle_check(specs[spec.spec_type][dependent], specs, new_upstream)

def _validate_cycle_free(specs):
    for spec_type in ['apps', 'libs']:
        for spec in specs[spec_type].values():
            _cycle_check(spec, specs, set([spec.name]))

def validate_specs_from_path(specs_path):
    """
    Validates Dusty specs at the given path. The following checks are performed:
        -That the given path exists
        -That there are bundles in the given path
        -That the fields in the specs match those allowed in our schemas
        -That references to apps, libs, and services point at defined specs
        -That there are no cycles in app and lib dependencies
    """
    # Validation of fields with schemer is now down implicitly through get_specs_from_path
    # We are dealing with Dusty_Specs class in this file
    log_to_client("Validating specs at path {}".format(specs_path))
    if not os.path.exists(specs_path):
        raise RuntimeError("Specs path not found: {}".format(specs_path))
    specs = get_specs_from_path(specs_path)
    _check_bare_minimum(specs)
    _validate_spec_names(specs)
    _validate_cycle_free(specs)
    log_to_client("Validation Complete!")

def validate_specs():
    """
    Validates specs using the path configured in Dusty's configuration
    """
    validate_specs_from_path(get_specs_path())
