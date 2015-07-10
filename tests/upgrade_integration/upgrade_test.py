import subprocess
import shutil
from time import sleep

from unittest import TestCase

from dusty.commands.upgrade import _test_dusty_binary
from dusty import constants

from ..testcases import DustyIntegrationTestCase

class TestUpgrade(DustyIntegrationTestCase):
    def tearDown(self):
        super(TestUpgrade, self).tearDown()
        self.stop_daemon()

    def run_daemon_binary(self, path='./dist/dusty'):
        self.daemon_process = subprocess.Popen(args=[path, '-d', '--suppress-warnings'], stdout=subprocess.PIPE)
        sleep(1)

    def run_daemon_source(self):
        self.daemon_process = subprocess.Popen(args=['dusty', '-d', '--suppress-warnings'], stdout=subprocess.PIPE)
        sleep(1)

    def stop_daemon(self):
        self.daemon_process.terminate()

    def recreate_dusty_binary(self):
        subprocess.check_call(['./setup/create_binaries.sh'], stdout=subprocess.PIPE)

    def test_upgrade_2_1(self):
        self.run_daemon_binary()
        version = '0.2.1'
        output = self.run_command('version')
        self.assertInSameLine(output, 'daemon', 'version')
        output = self.run_command('upgrade {}'.format(version))
        self.assertInSameLine(output, 'Downloading', version)
        self.assertInSameLine(output, 'Finished upgrade', version)
        sleep(1)
        output = self.run_command('version', raise_on_error=False)
        self.assertInSameLine(output, 'daemon', 'version', version)
        self.assertInSameLine(output, 'client', 'version', constants.VERSION)
        self.recreate_dusty_binary()

    def test_upgrade_source_fails(self):
        self.run_daemon_source()
        output = ''
        output = self.run_command('upgrade')
        self.assertTrue('It looks like you\'re running Dusty from source' in output)
        output = self.run_command('version')
        self.assertInSameLine(output, 'daemon', 'version', constants.VERSION)

    def test_upgrade_bad_name_fails(self):
        shutil.copy('dist/dusty', 'dist/python')
        self.run_daemon_binary(path='./dist/python')
        output = ''
        with self.assertRaises(self.CommandError):
            output = self.run_command('upgrade')
        output = self.run_command('version')
        self.assertInSameLine(output, 'daemon', 'version', constants.VERSION)
