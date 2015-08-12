import os
import tempfile
import textwrap

import dusty.constants
from dusty.systems import config_file
from ....testcases import DustyTestCase

class TestConfigFileSystem(DustyTestCase):
    def setUp(self):
        super(TestConfigFileSystem, self).setUp()
        self.spec_output = textwrap.dedent("""\
        # BEGIN section for Dusty
        127.0.0.1 local.gc.com
        127.0.0.2 local-api.gc.com
        # END section for Dusty
        """)
        self.non_spec_starter = "127.0.0.1 some-host.local.com\n"

    def test_remove_current_dusty_config_from_blank(self):
        result = config_file.remove_current_dusty_config(self.spec_output)
        self.assertEqual(result, "")

    def test_remove_current_dusty_config_from_starting(self):
        result = config_file.remove_current_dusty_config(self.non_spec_starter + self.spec_output)
        self.assertEqual(result, self.non_spec_starter)

    def test_remove_current_dusty_config_from_ending(self):
        result = config_file.remove_current_dusty_config(self.spec_output + self.non_spec_starter)
        self.assertEqual(result, self.non_spec_starter)

    def test_create_and_remove_section(self):
        contents = 'arbitrary contents'
        dusty_config = config_file.create_config_section(contents)
        stripped_config = config_file.remove_current_dusty_config(dusty_config)
        self.assertEqual(stripped_config, "")

    def test_get_dusty_config_section(self):
        dusty_contents = 'dusty contents!!\n'
        dusty_config = config_file.create_config_section(dusty_contents)
        file_contents = "leading stuff\n{}trailin_stuff".format(dusty_config)
        self.assertEqual(config_file.get_dusty_config_section(file_contents), dusty_contents)
