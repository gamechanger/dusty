from __future__ import absolute_import

import os
import sys
import shutil
import tempfile
import logging
import getpass
import subprocess
import threading
import time
from contextlib import contextmanager

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
from dusty.systems.nfs import client as nfs_client
from dusty.systems.nfs import server as nfs_server
from dusty.path import parent_dir
from dusty.subprocess import call_demoted
from .fixtures import basic_specs_fixture
from dusty.log import client_logger, DustyClientTestingSocketHandler
from dusty.memoize import reset_memoize_cache

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
        reset_memoize_cache()

    def tearDown(self):
        os.remove(self.temp_config_path)
        shutil.rmtree(self.temp_specs_path)
        shutil.rmtree(self.temp_repos_path)
        logging.getLogger(constants.SOCKET_LOGGER_NAME).removeHandler(self.capture_handler)
        reset_memoize_cache()

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

class SysExit(Exception):
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

        self.tests_user = os.getenv('DUSTY_INTEGRATION_TESTS_USER', self.current_user)
        save_config_value(constants.CONFIG_MAC_USERNAME_KEY, self.tests_user)

        override_repo(get_specs_repo().remote_path, self.overridden_specs_path)
        self.fake_local_repo_location = '/tmp/fake-repo'
        self._set_up_fake_local_repo('/tmp/fake-repo')
        self._clear_stdout()
        self.exec_docker_processes = []
        reset_memoize_cache()

    def tearDown(self):
        for exec_docker_process in self.exec_docker_processes:
            try:
                os.kill(exec_docker_process.pid)
            except:
                pass
        shutil.rmtree(self.overridden_specs_path)
        if os.path.exists(constants.COMPOSE_DIR):
            shutil.rmtree(constants.COMPOSE_DIR)
        shutil.rmtree('/tmp/fake-repo')
        save_config(self.previous_config)
        self.handler.log_to_client_output = ''
        client_logger.removeHandler(self.handler)
        nfs_client.unmount_all_repos()
        reset_memoize_cache()
        nfs_server._write_exports_config(set())

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
        out = sys.stdout.getvalue()[self.stdout_start:].strip()
        if isinstance(out, unicode):
            out = out.encode('utf-8')
        return out

    def exec_docker_patch(self, *args):
        docker_executable = subprocess.check_output('which docker', shell=True).rstrip('\n')
        args = [docker_executable] + [a for a in args]
        self.exec_docker_processes.append(subprocess.Popen(args=args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=get_docker_env()))

    @patch('sys.exit')
    def run_command(self, args, fake_exit, raise_on_error=True):
        """Run a command through the Dusty client entrypoint, e.g. simulating
        the Dusty CLI as close as possible without having to call a subprocess.
        This command raises if the command fails, otherwise it returns the
        stdout generated by the command."""
        with patch('dusty.commands.utils.exec_docker', wraps=self.exec_docker_patch) as fake_exec_docker:
            fake_exit.side_effect = SysExit('sys.exit called')
            self.fake_exec_docker = fake_exec_docker
            sys.argv = ['dusty'] + args.split(' ')
            try:
                client_entrypoint()
            except SysExit:
                pass
            for call in fake_exit.mock_calls:
                name, args, kwargs = call
                if len(args) == 1 and args[0] > 0 and raise_on_error:
                    self._clear_stdout()
                    raise CommandError('Command {} returned with exit code: {}'.format(' '.join(sys.argv), args[0]))
            result = self.stdout
            self._clear_stdout()
            return result

    def wait_for_exec_docker(self, timeout=3):
        def wait_for_processes():
            for p in self.exec_docker_processes:
                if p.poll() is None:
                    p.communicate()
        thread = threading.Thread(target=wait_for_processes)
        thread.start()
        thread.join(timeout)
        if thread.isAlive():
            raise RuntimeError('Exec docker processes didn\'t complete before timeout of {}s'.format(timeout))

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
        container = get_container_for_app_or_service(service_name, include_exited=include_exited)
        return bool(container)

    def _image_exists(self, image_to_find):
        client = get_docker_client()
        all_images = client.images(all=True)
        return any(image_to_find in image['RepoTags'] for image in all_images)

    def _file_exists_in_container(self, service_name, file_path):
        call_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME, 'sync']) # flush any outstanding writes
        file_exists_str = self.exec_in_container(service_name,
            'sh -c \'[ -f {} ] && echo "yes" || echo "no"\''.format(file_path)).rstrip()
        return file_exists_str == 'yes'

    def exec_in_container(self, service_name, command):
        container = get_container_for_app_or_service(service_name, raise_if_not_found=True)
        return exec_in_container(container, *command.split(' '))

    def remove_path_in_container(self, service_name, file_path):
        self.exec_in_container(service_name, 'rm -rf {}'.format(file_path))

    def write_file_in_container(self, service_name, file_path, contents):
        self.exec_in_container(service_name, 'mkdir -p {}'.format(parent_dir(file_path)))
        self.exec_in_container(service_name, 'sh -c "echo -n {} > {}"'.format(contents, file_path))

    def container_id(self, service_name):
        return get_container_for_app_or_service(service_name, include_exited=True, raise_if_not_found=True)['Id']

    def inspect_container(self, service_name):
        container_id = self.container_id(service_name)
        client = get_docker_client()
        return client.inspect_container(container_id)

    def remove_container(self, service_name):
        container_id = self.container_id(service_name)
        client = get_docker_client()
        client.remove_container(container_id, force=True)

    @staticmethod
    def retriable_assertion(backoff, max_retries):
        def retriable_fn_wrapper(fn):
            def retriable_fn(*args, **kwargs):
                for i in range(0, max_retries):
                    try:
                        return fn(*args, **kwargs)
                    except AssertionError:
                        print 'Retriable assertion failure {}'.format(i + 1)
                        if i == max_retries - 1:
                            raise
                    time.sleep(backoff)
            return retriable_fn
        return retriable_fn_wrapper

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

    def assertEnvInContainer(self, app_or_service, var, value):
        env = self.exec_in_container(app_or_service, 'printenv {}'.format(var)).rstrip()
        self.assertEqual(env, value)

    def assertEnvNotInContainer(self, app_or_service, var):
        env = self.exec_in_container(app_or_service, 'printenv {}'.format(var)).rstrip()
        self.assertEqual(env, '')

    @contextmanager
    def assertLogToClientOutput(self, expected_output):
        self.handler.log_to_client_output = ''
        try:
            yield
        finally:
            self.assertEqual(self.handler.log_to_client_output.rstrip(), expected_output)
