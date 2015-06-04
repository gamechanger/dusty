from ..testcases import DustyTestCase

from dusty.dusty_warnings import Warnings

class TestWarnings(DustyTestCase):
    def setUp(self):
        super(TestWarnings, self).setUp()
        self.warnings = Warnings()

    def test_warn(self):
        message_1 = 'Something is wrong, yo'
        message_2 = 'Yo this thing is also wrong'
        self.warnings.warn('test', message_1)
        self.assertItemsEqual(self.warnings._stored, {'test': [message_1]})
        self.warnings.warn('test', message_2)
        self.assertItemsEqual(self.warnings._stored, {'test': [message_1, message_2]})

    def test_has_warnings(self):
        self.assertFalse(self.warnings.has_warnings)
        self.warnings.warn('test', 'yo')
        self.assertTrue(self.warnings.has_warnings)

    def test_pretty_with_no_warnings(self):
        self.assertEqual(self.warnings.pretty(), "")

    def test_pretty(self):
        message_1 = 'Something is wrong, yo'
        message_2 = 'Something is very wrong, and that something takes way more than 80 characters to communicate the fact that it is wrong'
        self.warnings.warn('test', message_1)
        self.warnings.warn('test', message_2)
        self.assertEqual(self.warnings.pretty(), "WARNING (test): Something is wrong, yo\nWARNING (test): Something is very wrong, and that something takes way more than 80 characters to\ncommunicate the fact that it is wrong\n")

    def test_clear_namespace(self):
        self.warnings.warn('test', 'Something is wrong, yo')
        self.assertEqual(len(self.warnings._stored['test']), 1)
        self.warnings.clear_namespace('test')
        self.assertEqual(len(self.warnings._stored['test']), 0)

    def test_clear_namespace_leaves_others_unaffected(self):
        self.warnings.warn('test', 'Something is wrong, yo')
        self.assertEqual(len(self.warnings._stored['test']), 1)
        self.warnings.clear_namespace('some-other-namespace')
        self.assertEqual(len(self.warnings._stored['test']), 1)
