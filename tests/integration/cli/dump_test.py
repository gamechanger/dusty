from ...testcases import DustyIntegrationTestCase

class TestDumpCLI(DustyIntegrationTestCase):
    def test_dump(self):
        result = self.run_command('dump')
        self.assertInSameLine(result, 'COMMAND', 'Dusty Version')
