from .utils import DustyTestCase

from dusty.warnings import Warnings

class TestWarnings(DustyTestCase):
    def setUp(self):
        super(TestWarnings, self).setUp()
        self.warnings = Warnings()

    def test_warn(self):
        message_1 = 'Something is wrong, yo'
        message_2 = 'Yo this thing is also wrong'
        self.warnings.warn(message_1)
        self.assertEqual(self.warnings._stored, [message_1])
        self.warnings.warn(message_2)
        self.assertEqual(self.warnings._stored, [message_1, message_2])

    def test_has_warnings(self):
        self.assertFalse(self.warnings.has_warnings)
        self.warnings.warn('yo')
        self.assertTrue(self.warnings.has_warnings)

    def test_pretty_with_no_warnings(self):
        self.assertEqual(self.warnings.pretty(), "")

    def test_pretty(self):
        message_1 = 'Something is wrong, yo'
        message_2 = 'Something is very wrong, and that something takes way more than 80 characters to communicate the fact that it is wrong'
        self.warnings.warn(message_1)
        self.warnings.warn(message_2)
        self.assertEqual(self.warnings.pretty(), "WARNING: Something is wrong, yo\nWARNING: Something is very wrong, and that something takes way more than 80 characters to\ncommunicate the fact that it is wrong")
