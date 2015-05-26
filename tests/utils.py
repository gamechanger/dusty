import os
import shutil
import tempfile

from nose.tools import nottest

import dusty.constants
from dusty.config import write_default_config, save_config_value
from dusty.compiler.spec_assembler import get_specs_repo
from dusty.commands.repos import override_repo
from .fixtures import basic_specs_fixture

def run(generator):
    for result in generator:
        print result

@nottest
def setup_test(cls):
    import logging
    logging.error("FSDFLKS:DFJSL:FJSD:LF  sadfasdfasdf")
    cls.temp_config_path = tempfile.mkstemp()[1]
    cls.temp_specs_path = tempfile.mkdtemp()
    cls.temp_repos_path = tempfile.mkdtemp()
    dusty.constants.CONFIG_PATH = cls.temp_config_path
    write_default_config()
    save_config_value('specs_repo', 'github.com/org/dusty-specs')
    run(override_repo(get_specs_repo(), cls.temp_specs_path))
    basic_specs_fixture()

@nottest
def teardown_test(cls):
    os.remove(cls.temp_config_path)
    shutil.rmtree(cls.temp_specs_path)
    shutil.rmtree(cls.temp_repos_path)
