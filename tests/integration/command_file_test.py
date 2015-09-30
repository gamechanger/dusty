from ..fixtures import fixture_with_commands, specs_fixture_with_depends
from ..testcases import DustyIntegrationTestCase

class TestCommandFile(DustyIntegrationTestCase):
    def setUp(self):
        super(TestCommandFile, self).setUp()
        fixture_with_commands()
        self.run_command('bundles activate bundle-a')

    def tearDown(self):
        try:
            self.run_command('stop')
        except:
            pass
        try:
            self.remove_container('appa')
        except:
            pass
        super(TestCommandFile, self).tearDown()

    @DustyIntegrationTestCase.retriable_assertion(.1, 8)
    def assertContainerIsNotRunningRetriable(self, service_name):
        self.assertContainerIsNotRunning(service_name)

    def test_once_is_run_once(self):
        self.run_command('up')
        self.assertFileInContainer('appa', '/once_test_file')
        self.assertFileContentsInContainer('appa', '/once_test_file', 'once ran\n')
        self.run_command('restart appa')
        self.assertFileContentsInContainer('appa', '/once_test_file', 'once ran\n')

    def test_always_is_run_always(self):
        self.run_command('up')
        self.assertFileInContainer('appa', '/always_test_file')
        self.assertFileContentsInContainer('appa', '/always_test_file', 'always ran\n')
        self.run_command('restart appa')
        self.assertFileContentsInContainer('appa', '/always_test_file', 'always ran\nalways ran\n')

    def test_once_to_stdout(self):
        self.run_command('up')
        self.run_command('logs appa')
        output = self.exec_docker_processes[0].stdout.read()
        self.assertTrue('once ran' in output)

    def test_always_to_stdout(self):
        self.run_command('up')
        self.run_command('logs appa')
        output = self.exec_docker_processes[0].stdout.read()
        self.assertTrue('always ran' in output)

    def test_once_output_is_logged(self):
        self.run_command('up')
        self.assertFileContentsInContainer('appa', '/var/log/dusty_once_fn.log', 'once ran\n')

    def test_once_stops_on_error(self):
        fixture_with_commands(once_fail=True)
        self.run_command('up')
        self.run_command('logs appa')
        output = self.exec_docker_processes[0].stdout.read()
        self.assertTrue('once starting' in output)
        self.assertInSameLine(output, 'random-command', 'not found')
        self.assertFalse('once ran' in output)
        self.assertContainerIsNotRunningRetriable('appa')

    def test_always_stops_on_error(self):
        fixture_with_commands(always_fail=True)
        self.run_command('up')
        self.run_command('logs appa')
        output = self.exec_docker_processes[0].stdout.read()
        self.assertTrue('once ran' in output)
        self.assertTrue('always starting' in output)
        self.assertInSameLine(output, 'random-command', 'not found')
        self.assertFalse('always ran' in output)
        self.assertContainerIsNotRunning('appa')

    def test_test_recreate_stops_on_error(self):
        fixture_with_commands(test_fail=True)
        with self.assertRaises(self.CommandError):
            self.run_command('test --recreate appa test')
        self.assertTrue('tests starting' in self.handler.log_to_client_output)
        self.assertInSameLine(self.handler.log_to_client_output, 'random-command', 'not found')
        self.assertFalse('tests running' in self.handler.log_to_client_output)
        self.assertFalse('tests passed' in self.handler.log_to_client_output)

    def test_app_hosts_are_added(self):
        specs_fixture_with_depends()
        self.run_command('bundles activate bundle-b')
        self.run_command('up --no-pull')
        hosts_contents = self.exec_in_container('appa', 'cat /etc/hosts')
        ip_route = self.exec_in_container('appa', 'ip route')
        dockerhost = filter(lambda line: 'default' in line, ip_route.splitlines())[0].split()[2]
        self.assertInSameLine(hosts_contents, 'local.appc.com', dockerhost)
