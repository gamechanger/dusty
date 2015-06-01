from unittest import TestCase

from schemer import ValidationException

from dusty.commands.validate import _ensure_app_build_or_image, _validate_app_references, _validate_cycle_free

class ValidatorTest(TestCase):
    def test_only_build_or_image(self):
        with self.assertRaises(ValidationException):
            _ensure_app_build_or_image({'image': 'gcimage', 'build': 'build.sh'})

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
        with self.assertRaises(AssertionError):
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
        with self.assertRaises(AssertionError):
            _validate_app_references(specs['apps']['app1'], specs)

    def test_validate_app_with_bad_lib(self):
        specs = {'apps': {
                'app1': {
                    'depends': {
                        'libs': [
                            'lib2',
                        ]
                    }
                }
            },
            'libs': {
                'lib1': {}
            }
        }
        with self.assertRaises(AssertionError):
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
        with self.assertRaises(ValidationException):
            _validate_cycle_free(specs)

    def test_lib_cycle_detection(self):
        specs = {'libs': {
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
        with self.assertRaises(ValidationException):
            _validate_cycle_free(specs)
