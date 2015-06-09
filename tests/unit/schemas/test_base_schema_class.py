from unittest import TestCase
from schemer import Schema, Array, ValidationException
from dusty.schemas.base_schema_class import DustySchema


class TestDustySchemaClass(TestCase):
    def setUp(self):
        self.base_schema = Schema({'street': {'type': basestring},
                                   'house_number': {'type': int, 'default': 1}})
        self.bigger_schema = Schema({'address': {'type': self.base_schema, 'default': {}},
                                     'first_name': {'type': basestring, 'required': True},
                                     'last_name': {'type': basestring, 'default': 'johnson'}})

    def test_init_invalid_doc(self):
        doc = {'street': 'dogstoon',
               'house_number': '1'}
        with self.assertRaises(ValidationException):
            DustySchema(self.base_schema, doc)

    def test_valid_doc(self):
        doc = {'street': 'dogstoon',
               'house_number': 1}
        dusty_schema = DustySchema(self.base_schema, doc)
        self.assertEquals(dusty_schema['street'], 'dogstoon')
        self.assertEquals(dusty_schema['house_number'], 1)

    def test_setting_defaults(self):
        doc = {'street': 'dogstoon'}
        dusty_schema = DustySchema(self.base_schema, doc)
        self.assertEquals(dusty_schema['street'], 'dogstoon')
        self.assertEquals(dusty_schema['house_number'], 1)

    def test_setting_defaults_more_complicated_1(self):
        doc = {'first_name': 'dusty'}
        dusty_schema = DustySchema(self.bigger_schema, doc)
        self.assertEquals(dusty_schema['first_name'], 'dusty')
        self.assertEquals(dusty_schema['last_name'], 'johnson')
        self.assertEquals(dusty_schema['address'], {'house_number': 1})

    def test_setting_defaults_more_complicated_2(self):
        doc = {'first_name': 'dusty',
               'address': {'street': 'dogstoon'}}
        dusty_schema = DustySchema(self.bigger_schema, doc)
        self.assertEquals(dusty_schema['address']['street'], 'dogstoon')
        self.assertEquals(dusty_schema['address']['house_number'], 1)
