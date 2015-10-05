from mock import Mock

from ..testcases import DustyTestCase
from ..fixtures import basic_specs_fixture
from dusty.config import get_config_value
from dusty.changeset import RepoChangeSet
from dusty import constants
from dusty.source import Repo

class TestRepoChangeset(DustyTestCase):
    def setUp(self):
        super(TestRepoChangeset, self).setUp()
        basic_specs_fixture()
        self.changeset = RepoChangeSet('testing', 'app-a')

        mocks = set()
        for repo in self.changeset.repos:
            mock_repo = Mock()
            mock_repo.remote_path = repo.remote_path
            mock_repo.local_commit_sha = 'sha_{}'.format(repo.remote_path)
            mocks.add(mock_repo)
        self.changeset.repos = mocks

    def test_init_on_app_with_no_libs(self):
        new = RepoChangeSet('new', 'app-b')
        self.assertEqual(len(new.repos), 1)
        self.assertIn(Repo('github.com/app/b'), new.repos)

    def test_init_on_app_with_libs(self):
        new = RepoChangeSet('new', 'app-a')
        self.assertEqual(len(new.repos), 2)
        self.assertIn(Repo('github.com/app/a'), new.repos)
        self.assertIn(Repo('github.com/lib/a'), new.repos)

    def test_init_on_lib(self):
        new = RepoChangeSet('new', 'lib-a')
        self.assertEqual(len(new.repos), 1)
        self.assertIn(Repo('github.com/lib/a'), new.repos)

    def test_has_changed_when_empty(self):
        self.assertTrue(self.changeset.has_changed())

    def test_has_changed_after_save(self):
        self.changeset.update()
        self.assertFalse(self.changeset.has_changed())

    def test_update(self):
        current_config = get_config_value(constants.CONFIG_CHANGESET_KEY) or {}
        self.assertIsNone(current_config.get(self.changeset.set_key))
        self.changeset.update()
        expected = {'app-a': {'github.com/app/a': 'sha_github.com/app/a', 'github.com/lib/a': 'sha_github.com/lib/a'}}
        updated_config = get_config_value(constants.CONFIG_CHANGESET_KEY) or {}
        self.assertItemsEqual(expected, updated_config.get(self.changeset.set_key))
