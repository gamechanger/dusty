from os import path
from shutil import rmtree
from subprocess import check_call
from tempfile import mkdtemp

import git

from dusty import constants
from dusty.log import log_to_client
from ...fixtures import busybox_single_app_bundle_fixture
from ...testcases import DustyIntegrationTestCase


class TestReposCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestReposCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)
        self.run_command('bundles activate busyboxa')
        self.temp_repos_dir = mkdtemp()
        self.old_repos_dir = constants.REPOS_DIR
        constants.REPOS_DIR = self.temp_repos_dir
        self.fake_local_repo_location_1 = path.join(mkdtemp(), 'fake-repo')
        self._set_up_fake_local_repo(path=self.fake_local_repo_location_1)
        self.fake_from_dir = mkdtemp()
        self.fake_from_repo_location = path.join(self.fake_from_dir, 'fake-repo')
        self._set_up_fake_local_repo(path=self.fake_from_repo_location)

    def tearDown(self):
        self.run_command('bundles deactivate busyboxa')
        constants.REPOS_DIR = self.old_repos_dir
        rmtree(self.fake_local_repo_location_1)
        rmtree(self.fake_from_dir)
        rmtree(self.temp_repos_dir)
        super(TestReposCLI, self).tearDown()

    def test_repos_list(self):
        result = self.run_command('repos list')
        self.assertInSameLine(result, 'github.com/gamechanger/dusty-example-specs', 'dusty-example-specs', self.overridden_specs_path)
        self.assertInSameLine(result, self.fake_local_repo_location, 'fake-repo')

    def test_repos_override(self):
        result = self.run_command('repos list')
        self.assertInSameLine(result, 'fake-repo', self.fake_local_repo_location)
        self.assertNotInSameLine(result, 'fake-repo', self.fake_local_repo_location_1)
        self.run_command('repos override fake-repo {}'.format(self.fake_local_repo_location_1))
        result = self.run_command('repos list')
        self.assertInSameLine(result, self.fake_local_repo_location, 'fake-repo', self.fake_local_repo_location_1)

    def test_repos_manage(self):
        self.run_command('repos override fake-repo {}'.format(self.fake_local_repo_location_1))
        result = self.run_command('repos list')
        self.assertInSameLine(result, self.fake_local_repo_location, 'fake-repo', self.fake_local_repo_location)
        result = self.run_command('repos manage fake-repo')
        self.assertNotInSameLine(result, 'fake-repo', self.fake_local_repo_location_1)
        self.assertInSameLine(result, 'fake-repo', self.fake_local_repo_location)

    def test_repos_from(self):
        self.run_command('repos from {}'.format(self.fake_from_dir))
        result = self.run_command('repos list')
        self.assertInSameLine(result, self.fake_local_repo_location, 'fake-repo', self.fake_from_repo_location)
        self.run_command('repos manage {}'.format(self.fake_local_repo_location))

    def test_repos_update(self):
        git_repo = git.Repo(self.fake_local_repo_location_1)
        target_file = path.join(self.fake_local_repo_location_1, 'car')
        check_call(['touch', target_file])
        self.assertFalse(path.isfile(path.join(constants.REPOS_DIR, target_file[1:])))
        self.run_command('repos override fake-repo {}'.format(self.fake_local_repo_location_1))
        git_repo.index.add([target_file])
        git_repo.index.commit('Second commit')
        self.run_command('repos update')
        self.assertTrue(path.isfile(path.join(constants.REPOS_DIR, target_file)))
