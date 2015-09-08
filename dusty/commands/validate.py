from copy import copy
import os

from schemer import ValidationException

from ..compiler.spec_assembler import get_specs_path, get_specs_from_path
from ..log import log_to_client
from ..schemas import app_schema, bundle_schema, lib_schema
from ..schemas.base_schema_class import notifies_validation_exception
from .. import constants
from ..payload import daemon_command

def _check_bare_minimum(specs):
    if not specs.get('bundles'):
        raise ValidationException("No Bundles found - exiting")

@notifies_validation_exception
def _validate_app_references(app, specs):
    for spec_type in ['apps', 'libs', 'services']:
        dependent = app['depends'][spec_type]
        if spec_type in ['apps', 'services']:
            dependent += app['conditional_links'][spec_type]
        not_present = set(dependent) - set(specs[spec_type].keys())
        if not_present:
            raise ValidationException('{} {} are not present in your specs'.format(spec_type, ', '.join(not_present)))

@notifies_validation_exception
def _validate_bundle_references(bundle, specs):
    not_present = set(bundle['apps']) - set(specs['apps'].keys())
    if not_present:
        raise ValidationException('Apps {} are not present in your specs'.format(', '.join(not_present)))

@notifies_validation_exception
def _validate_lib_references(lib, specs):
    not_present = set(lib['depends']['libs']) - set(specs['libs'].keys())
    if not_present:
        raise ValidationException('Libs {} are not present in your specs'.format(', '.join(not_present)))

def _check_nginx_name_conflict(specs):
    apps = set(specs['apps'].keys())
    services = set(specs['services'].keys())
    if constants.DUSTY_NGINX_NAME in apps.union(services):
        raise ValidationException('The name {} is reserved for use by Dusty\'s internal nginx - please choose a different name'.format(constants.DUSTY_NGINX_NAME))

def _check_name_overlap(specs):
    apps = set(specs['apps'].keys())
    libs = set(specs['libs'].keys())
    services = set(specs['services'].keys())
    app_service_overlap = apps.intersection(services)
    if app_service_overlap:
        raise ValidationException('Apps and services cannot share names: {}'.format(app_service_overlap))
    app_lib_overlap = apps.intersection(libs)
    if app_lib_overlap:
        raise ValidationException('Apps and libs cannot share names: {}'.format(app_lib_overlap))
    service_lib_overlap = services.intersection(libs)
    if service_lib_overlap:
        raise ValidationException('Services and libs cannot share names: {}'.format(service_lib_overlap))

def _validate_spec_names(specs):
    _check_name_overlap(specs)
    _check_nginx_name_conflict(specs)
    for app in specs['apps'].values():
        _validate_app_references(app, specs)
    for bundle in specs['bundles'].values():
        _validate_bundle_references(bundle, specs)
    for lib in specs['libs'].values():
        _validate_lib_references(lib, specs)

def _cycle_check(spec, specs, upstream):
    for dependent in spec['depends'][spec.spec_type]:
        if dependent in upstream:
            raise ValidationException("Cycle found for {0} {1}.  Upstream: {2}".format(spec.type_singular, spec.name, upstream))
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

@daemon_command
def validate_specs():
    """
    Validates specs using the path configured in Dusty's configuration
    """
    validate_specs_from_path(get_specs_path())
