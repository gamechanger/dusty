import os
import sys
import shutil
import tempfile
import logging
import getpass
import subprocess

from unittest import TestCase
from nose.tools import nottest
from mock import patch
import git

from dusty import constants
from dusty.config import write_default_config, save_config_value, get_config, save_config
from dusty.compiler.spec_assembler import get_specs_repo
from dusty.commands.repos import override_repo
from dusty.cli import main as client_entrypoint
from dusty.schemas.base_schema_class import get_specs_from_path, DustySpecs
from dusty.systems.docker import exec_in_container, get_docker_client, get_container_for_app_or_service, get_docker_env
from dusty.path import parent_dir
from .fixtures import basic_specs_fixture
from dusty.log import client_logger, DustyClientTestingSocketHandler

class TestCaptureHandler(logging.Handler):
    def __init__(self, lst):
        super(TestCaptureHandler, self).__init__()
        self.lst = lst

    def emit(self, record):
        self.lst.append(self.format(record))

class DustyTestCase(TestCase):
    def setUp(self):
        self.temp_config_path = tempfile.mkstemp()[1]
        self.temp_specs_path = tempfile.mkdtemp()
        self.temp_repos_path = tempfile.mkdtemp()

        constants.CONFIG_PATH = self.temp_config_path
        write_default_config()
        save_config_value(constants.CONFIG_SPECS_REPO_KEY, 'github.com/org/dusty-specs')
        override_repo(get_specs_repo().remote_path, self.temp_specs_path)
        basic_specs_fixture()

        self.client_output = []
        self.capture_handler = TestCaptureHandler(self.client_output)
        logging.getLogger(constants.SOCKET_LOGGER_NAME).addHandler(self.capture_handler)

    def tearDown(self):
        os.remove(self.temp_config_path)
        shutil.rmtree(self.temp_specs_path)
        shutil.rmtree(self.temp_repos_path)
        logging.getLogger(constants.SOCKET_LOGGER_NAME).removeHandler(self.capture_handler)

    @nottest
    @patch('dusty.schemas.base_schema_class.get_specs_from_path')
    def make_test_specs(self, specs_dict, fake_specs_from_path):
        fake_specs_from_path.return_value = specs_dict
        return DustySpecs('')

    @property
    def last_client_output(self):
        return self.client_output[-1] if self.client_output else None

class CommandError(Exception):
    pass

class DustyIntegrationTestCase(TestCase):
    """This test case intentionally avoids mocking whenever possible
    in order to get as close as possible to the actual state that
    would be experienced on a system running Dusty. Therefore,
    integration tests are possibly destructive if run on a user's
    machine. To help protect the user from running them accidentally,
    integration tests will refuse to run unless the environment
    variable DUSTY_ALLOW_INTEGRATION_TESTS is set.

    Note that this also assumes it is running against an actual
    Dusty daemon process on the local host."""
    def setUp(self):
        if not os.getenv('DUSTY_ALLOW_INTEGRATION_TESTS'):
            raise RuntimeError('You must set the env var DUSTY_ALLOW_INTEGRATION_TESTS to run integration tests. '
                               'This may affect your local config, do not run integration tests on your actual '
                               "machine unless you know what you're doing!")
        self.handler = DustyClientTestingSocketHandler()
        client_logger.addHandler(self.handler)
        self.previous_config = get_config()
        self._clear_stdout()
        self.overridden_specs_path = tempfile.mkdtemp()
        write_default_config()
        save_config_value(constants.CONFIG_SETUP_KEY, True)
        save_config_value(constants.CONFIG_SPECS_REPO_KEY, 'github.com/gamechanger/dusty-example-specs')
        save_config_value(constants.CONFIG_MAC_USERNAME_KEY, self.current_user)
        override_repo(get_specs_repo().remote_path, self.overridden_specs_path)
        self.fake_local_repo_location = '/tmp/fake-repo'
        self._set_up_fake_local_repo('/tmp/fake-repo')
        self._clear_stdout()
        self.exec_docker_processes = []

    def tearDown(self):
        for exec_docker_process in self.exec_docker_processes:
            try:
                os.kill(exec_docker_process.pid)
            except:
                pass
        shutil.rmtree(self.overridden_specs_path)
        if os.path.exists(constants.REPOS_DIR):
            shutil.rmtree(constants.REPOS_DIR)
        if os.path.exists(constants.COMPOSE_DIR):
            shutil.rmtree(constants.COMPOSE_DIR)
        shutil.rmtree('/tmp/fake-repo')
        save_config(self.previous_config)
        self.handler.log_to_client_output = ''
        client_logger.removeHandler(self.handler)

    def _clear_stdout(self):
        self.stdout_start = len(sys.stdout.getvalue())

    @property
    def current_user(self):
        return getpass.getuser()

    @property
    def CommandError(self):
        """Pure convenience to avoid having to import this explicitly"""
        return CommandError

    @property
    def stdout(self):
        """Returns any stdout that has been generated *since* the last time
        clear_stdout was called."""
        return sys.stdout.getvalue()[self.stdout_start:].strip()

    def exec_docker_patch(self, *args):
        args = ['docker'] + [a for a in args]
        self.exec_docker_processes.append(subprocess.Popen(args=args, stdout=subprocess.PIPE, env=get_docker_env(), shell=True))

    @patch('sys.exit')
    def run_command(self, args, fake_exit):
        """Run a command through the Dusty client entrypoint, e.g. simulating
        the Dusty CLI as close as possible without having to call a subprocess.
        This command raises if the command fails, otherwise it returns the
        stdout generated by the command."""
        with patch('dusty.commands.utils.exec_docker', wraps=self.exec_docker_patch) as fake_exec_docker:
            self.fake_exec_docker = fake_exec_docker
            sys.argv = ['dusty'] + args.split(' ')
            client_entrypoint()
            for call in fake_exit.mock_calls:
                name, args, kwargs = call
                if len(args) == 1 and args[0] > 0:
                    self._clear_stdout()
                    raise CommandError('Command {} returned with exit code: {}'.format(' '.join(sys.argv), args[0]))
            result = self.stdout
            self._clear_stdout()
            return result

    def _set_up_fake_local_repo(self, path='/tmp/fake-repo'):
        repo = git.Repo.init(path)
        with open(os.path.join(path, 'README.md'), 'w') as f:
            f.write('# {}'.format(path.split('/')[-1]))
        repo.index.add([os.path.join(path, 'README.md')])
        repo.index.commit('Initial commit')

    def _in_same_line(self, string, *values):
        for line in string.splitlines():
            if all(value in line for value in values):
                return True
        return False

    def _container_exists_in_set(self, service_name, include_exited):
        client = get_docker_client()
        container = get_container_for_app_or_service(client, service_name, include_exited=include_exited)
        return bool(container)

    def _image_exists(self, image_to_find):
        client = get_docker_client()
        all_images = client.images(all=True)
        return any(image_to_find in image['RepoTags'] for image in all_images)

    def _file_exists_in_container(self, service_name, file_path):
        file_exists_str = self.exec_in_container(service_name,
            'sh -c \'[ -f {} ] && echo "yes" || echo "no"\''.format(file_path)).rstrip()
        return file_exists_str == 'yes'

    def exec_in_container(self, service_name, command):
        client = get_docker_client()
        container = get_container_for_app_or_service(client, service_name, raise_if_not_found=True)
        return exec_in_container(client, container, *command.split(' '))

    def remove_path_in_container(self, service_name, file_path):
        self.exec_in_container(service_name, 'rm -rf {}'.format(file_path))

    def write_file_in_container(self, service_name, file_path, contents):
        self.exec_in_container(service_name, 'mkdir -p {}'.format(parent_dir(file_path)))
        self.exec_in_container(service_name, 'sh -c "echo -n {} > {}"'.format(contents, file_path))

    def container_id(self, service_name):
        client = get_docker_client()
        return get_container_for_app_or_service(client, service_name, include_exited=True, raise_if_not_found=True)['Id']

    def inspect_container(self, service_name):
        container_id = self.container_id(service_name)
        client = get_docker_client()
        return client.inspect_container(container_id)

    def assertInSameLine(self, string, *values):
        self.assertTrue(self._in_same_line(string, *values))

    def assertNotInSameLine(self, string, *values):
        self.assertFalse(self._in_same_line(string, *values))

    def assertFileContents(self, file_path, contents):
        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), contents)

    def assertFileContentsInContainer(self, service_name, file_path, contents):
        self.assertEqual(self.exec_in_container(service_name, 'cat {}'.format(file_path)), contents)

    def assertFileNotInContainer(self, service_name, file_path):
        self.assertFalse(self._file_exists_in_container(service_name, file_path))

    def assertFileInContainer(self, service_name, file_path):
        self.assertTrue(self._file_exists_in_container(service_name, file_path))

    def assertContainerRunning(self, service_name):
        self.assertTrue(self._container_exists_in_set(service_name, False))

    def assertContainerIsNotRunning(self, service_name):
        self.assertFalse(self._container_exists_in_set(service_name, False))

    def assertContainerExists(self, service_name):
        self.assertTrue(self._container_exists_in_set(service_name, True))

    def assertContainerDoesNotExist(self, service_name):
        self.assertFalse(self._container_exists_in_set(service_name, True))

    def assertImageExists(self, image):
        self.assertTrue(self._image_exists(image))

    def assertImageDoesNotExist(self, image):
        self.assertFalse(self._image_exists(image))

    def assertExecDocker(self, *args):
        self.fake_exec_docker.assert_called_with(*args)

    def assertConfigValue(self, key, value):
        config = get_config()
        self.assertEqual(config[key], value)
