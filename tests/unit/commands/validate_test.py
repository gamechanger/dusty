from unittest import TestCase
from schemer import ValidationException

from ..utils import get_app_dusty_schema, get_lib_dusty_schema
from dusty.commands.validate import (_validate_app_references, _validate_cycle_free)
from dusty import constants

class ValidatorTest(TestCase):
    def test_validate_app_with_bad_service(self):
        specs = {'apps': {
                'app1': get_app_dusty_schema({
                    'depends': {
                        'services': [
                            'service1',
                            'service2'
                        ]
                    }
                })
            },
            'services': {
                'service1': {}
            }
        }
        with self.assertRaises(AssertionError):
            _validate_app_references(specs['apps']['app1'], specs)

    def test_validate_app_with_bad_app(self):
        specs = {'apps': {
                'app1': get_app_dusty_schema({
                    'depends': {
                        'apps': [
                            'app3',
                        ]
                    }
                }),
                'app2': get_app_dusty_schema({})
            }
        }
        with self.assertRaises(AssertionError):
            _validate_app_references(specs['apps']['app1'], specs)

    def test_validate_app_with_bad_lib(self):
        specs = {'apps': {
                'app1': get_app_dusty_schema({
                    'depends': {
                        'libs': [
                            'lib2',
                        ]
                    }
                })
            },
            'libs': {
                'lib1': get_lib_dusty_schema({})
            }
        }
        with self.assertRaises(AssertionError):
            _validate_app_references(specs['apps']['app1'], specs)

    def test_app_cycle_detection(self):
        specs = {'apps': {
                'app1': get_app_dusty_schema({
                    'depends': {
                        'apps': [
                            'app1',
                        ]
                    }
                })
            }
        }
        with self.assertRaises(ValidationException):
            _validate_cycle_free(specs)

    def test_lib_cycle_detection(self):
        specs = {
        'apps': {},
        'libs': {
                'lib1': get_lib_dusty_schema({
                    'depends': {
                        'libs': [
                            'lib2',
                        ]
                    }
                }),
                'lib2': get_lib_dusty_schema({
                    'depends': {
                        'libs': [
                            'lib3',
                        ]
                    }
                }),
                'lib3': get_lib_dusty_schema({
                    'depends': {
                        'libs': [
                            'lib1',
                        ]
                    }
                })
            }
        }
        with self.assertRaises(ValidationException):
            _validate_cycle_free(specs)
