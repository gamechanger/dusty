import os
from shutil import rmtree
from subprocess import check_call
from tempfile import mkdtemp

import git

from dusty import constants
from dusty.log import log_to_client
from ...fixtures import busybox_single_app_bundle_fixture, single_specs_fixture
from ...testcases import DustyIntegrationTestCase


class TestReposCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestReposCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)
        single_specs_fixture()

        self.temp_repos_dir = mkdtemp()
        self.fake_override_dir = mkdtemp()
        self.fake_from_dir = mkdtemp()

        os.chmod(self.temp_repos_dir, 0777)
        os.chmod(self.fake_override_dir, 0777)
        os.chmod(self.fake_from_dir, 0777)

        self.fake_override_repo_location = os.path.join(self.fake_override_dir, 'fake-repo')
        self._set_up_fake_local_repo(path=self.fake_override_repo_location)
        self.fake_from_repo_location = os.path.join(self.fake_from_dir, 'fake-repo')
        self._set_up_fake_local_repo(path=self.fake_from_repo_location)
        self.fake_source_repo_location = '/tmp/fake-repo'
        self._set_up_fake_local_repo(path=self.fake_source_repo_location)

    def tearDown(self):
        rmtree(self.temp_repos_dir)
        rmtree(self.fake_override_dir)
        rmtree(self.fake_from_dir)
        rmtree(os.path.join(constants.REPOS_DIR), self.fake_source_repo_location.strip('/'))
        super(TestReposCLI, self).tearDown()

    def test_repos_list(self):
        result = self.run_command('repos list')
        self.assertInSameLine(result, 'github.com/gamechanger/dusty-example-specs', 'dusty-example-specs', self.overridden_specs_path)
        self.assertInSameLine(result, self.fake_local_repo_location, 'fake-repo')

    def test_repos_override(self):
        result = self.run_command('repos list')
        self.assertInSameLine(result, 'fake-repo', self.fake_local_repo_location)
        self.assertNotInSameLine(result, 'fake-repo', self.fake_override_repo_location)
        self.run_command('repos override fake-repo {}'.format(self.fake_override_repo_location))
        result = self.run_command('repos list')
        self.assertInSameLine(result, self.fake_local_repo_location, 'fake-repo', self.fake_override_repo_location)

    def test_repos_manage(self):
        self.run_command('repos override fake-repo {}'.format(self.fake_override_repo_location))
        result = self.run_command('repos list')
        self.assertInSameLine(result, self.fake_local_repo_location, 'fake-repo', self.fake_local_repo_location)
        result = self.run_command('repos manage fake-repo')
        self.assertNotInSameLine(result, 'fake-repo', self.fake_override_repo_location)
        self.assertInSameLine(result, 'fake-repo', self.fake_local_repo_location)

    def test_repos_manage_all_with_one(self):
        self.run_command('repos override fake-repo {}'.format(self.fake_override_repo_location))
        result = self.run_command('repos list')
        self.assertInSameLine(result, self.fake_override_repo_location, 'fake-repo')
        self.run_command('repos manage --all')
        result = self.run_command('repos list')
        self.assertNotInSameLine(result, self.fake_override_repo_location, 'fake-repo')


    def test_repos_manage_all_with_multiple(self):
        self.run_command('repos override fake-repo {}'.format(self.fake_override_repo_location))
        self.run_command('repos override github.com/app/a {}'.format(self.fake_from_repo_location))
        result = self.run_command('repos list')
        self.assertInSameLine(result, self.fake_override_repo_location, 'fake-repo')
        self.assertInSameLine(result, self.fake_from_repo_location, 'github.com/app/a')
        self.run_command('repos manage --all')
        result = self.run_command('repos list')
        self.assertNotInSameLine(result, self.fake_override_repo_location, 'fake-repo')
        self.assertNotInSameLine(result, self.fake_from_repo_location, 'github.com/app/a')

    def test_repos_from(self):
        self.run_command('repos from {}'.format(self.fake_from_dir))
        result = self.run_command('repos list')
        self.assertInSameLine(result, self.fake_local_repo_location, 'fake-repo', self.fake_from_repo_location)
        self.run_command('repos manage fake-repo')

    def test_repos_update(self):
        git_repo = git.Repo(self.fake_source_repo_location)
        target_file = os.path.join(self.fake_source_repo_location, 'car')
        check_call(['touch', target_file])
        self.assertFalse(os.path.isfile(os.path.join(constants.REPOS_DIR, target_file.strip('/'))))
        git_repo.index.add([target_file])
        git_repo.index.commit('Second commit')
        self.run_command('bundles activate busyboxa')
        self.run_command('repos update')
        self.assertTrue(os.path.isfile(os.path.join(constants.REPOS_DIR, target_file.strip('/'))))

    def test_repos_update_failure(self):
        git_repo = git.Repo(self.fake_source_repo_location)
        remote_file = os.path.join(self.fake_source_repo_location, 'bus')
        local_conflict = os.path.join(constants.REPOS_DIR, remote_file.strip('/'))
        self.run_command('bundles activate busyboxa')
        output = self.run_command('repos update')
        check_call(['touch', remote_file])
        check_call(['touch', local_conflict])
        git_repo.index.add([remote_file])
        git_repo.index.commit('Second commit')
        self.run_command('bundles activate busyboxa')
        output = self.run_command('repos update')
        self.assertInSameLine(output, 'WARNING', 'fake-repo', 'local conflicts')
