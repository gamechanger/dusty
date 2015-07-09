from schemer import ValidationException

from ...testcases import DustyTestCase
from ..utils import apply_required_keys
from dusty.commands.validate import (_validate_app_references, _validate_cycle_free,
                                     _check_name_overlap)
from dusty import constants

class ValidatorTest(DustyTestCase):
    def test_validate_app_with_bad_service(self):
        specs = {'apps': {
                'app1': {
                    'depends': {
                        'services': [
                            'service1',
                            'service2'
                        ]
                    }
                }
            },
            'services': {
                'service1': {}
            }
        }
        apply_required_keys(specs)
        specs = self.make_test_specs(specs)
        with self.assertRaises(ValidationException):
            _validate_app_references(specs['apps']['app1'], specs)

    def test_validate_app_with_bad_app(self):
        specs = {'apps': {
                'app1': {
                    'depends': {
                        'apps': [
                            'app3',
                        ]
                    }
                },
                'app2': {}
            }
        }
        apply_required_keys(specs)
        specs = self.make_test_specs(specs)
        with self.assertRaises(ValidationException):
            _validate_app_references(specs['apps']['app1'], specs)

    def test_validate_app_with_bad_lib(self):
        specs = {'apps': {
                'app1': {
                    'depends': {
                        'libs': [
                            'lib2',
                        ]
                    }
                },
            },
            'libs': {
                'lib1': {}
            }
        }
        apply_required_keys(specs)
        specs = self.make_test_specs(specs)
        with self.assertRaises(ValidationException):
            _validate_app_references(specs['apps']['app1'], specs)

    def test_app_cycle_detection(self):
        specs = {'apps': {
                'app1': {
                    'depends': {
                        'apps': [
                            'app1',
                        ]
                    }
                }
            }
        }
        apply_required_keys(specs)
        specs = self.make_test_specs(specs)
        with self.assertRaises(ValidationException):
            _validate_cycle_free(specs)

    def test_lib_cycle_detection(self):
        specs = {
        'apps': {},
        'libs': {
                'lib1': {
                    'depends': {
                        'libs': [
                            'lib2',
                        ]
                    }
                },
                'lib2': {
                    'depends': {
                        'libs': [
                            'lib3',
                        ]
                    }
                },
                'lib3': {
                    'depends': {
                        'libs': [
                            'lib1',
                        ]
                    }
                }
            }
        }
        apply_required_keys(specs)
        specs = self.make_test_specs(specs)
        with self.assertRaises(ValidationException):
            _validate_cycle_free(specs)

    def test_app_lib_unique_detection(self):
        specs = {'apps': {
                    'overlap': {
                    },
                },
                'libs': {
                    'overlap': {
                    },
                }
        }
        apply_required_keys(specs)
        specs = self.make_test_specs(specs)
        with self.assertRaises(ValidationException):
            _check_name_overlap(specs)


    def test_app_service_unique_detection(self):
        specs = {'apps': {
                    'overlap': {
                    },
                },
                'services': {
                    'overlap': {
                    },
                }
        }
        apply_required_keys(specs)
        specs = self.make_test_specs(specs)
        with self.assertRaises(ValidationException):
            _check_name_overlap(specs)
