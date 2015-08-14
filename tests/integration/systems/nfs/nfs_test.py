from __future__ import absolute_import

import os
from shutil import rmtree
from subprocess import CalledProcessError
from tempfile import mkdtemp
import time

from dusty import constants
from dusty.source import Repo
from dusty.systems.nfs import client, server
from dusty.subprocess import check_and_log_output_and_error
from ....testcases import DustyIntegrationTestCase
from ....fixtures import single_specs_fixture

NFS_SLEEP = .3

class TestNFS(DustyIntegrationTestCase):
    def setUp(self):
        super(TestNFS, self).setUp()

        self.fake_override_dir = mkdtemp()
        self.fake_override_repo_location = os.path.join(self.fake_override_dir, 'a')
        os.makedirs(self.fake_override_repo_location)

        single_specs_fixture()

    def tearDown(self):
        if os.path.exists(constants.EXPORTS_PATH):
            os.remove(constants.EXPORTS_PATH)
        rmtree(self.fake_override_dir)
        try:
            self.run_command('stop --rm')
            self.run_command('repos manage --all')
        except:
            pass

        super(TestNFS, self).tearDown()

    def test_managed_repo_mount(self):
        local_dir = Repo('github.com/app/a').managed_path
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        self.run_command('bundles activate bundle-a')
        self.run_command('up --no-pull')
        self.run_command('scripts appa example')
        time.sleep(NFS_SLEEP)
        self.assertTrue(os.path.isfile(os.path.join(local_dir, 'foo')))

    def test_overridden_repo_mount(self):
        self.run_command('bundles activate bundle-a')
        self.run_command('repos override a {}'.format(self.fake_override_repo_location))
        self.run_command('up --no-pull')
        self.run_command('scripts appa example')
        time.sleep(NFS_SLEEP)
        self.assertTrue(os.path.isfile(os.path.join(self.fake_override_repo_location, 'foo')))

    def test_root_file_ownership(self):
        os.chown(self.fake_override_repo_location, 0, 0)
        self.run_command('repos override a {}'.format(self.fake_override_repo_location))
        self.run_command('bundles activate bundle-a')
        self.run_command('up --no-pull')
        self.run_command('scripts appa example')
        time.sleep(NFS_SLEEP)
        stat = os.stat(os.path.join(self.fake_override_repo_location, 'foo'))
        self.assertEqual(stat.st_uid, 0)
        self.assertEqual(stat.st_gid, 0)

    def test_user_file_ownership(self):
        os.chown(self.fake_override_repo_location, 501, 20)
        self.run_command('repos override a {}'.format(self.fake_override_repo_location))
        self.run_command('bundles activate bundle-a')
        self.run_command('up --no-pull')
        self.run_command('scripts appa example')
        time.sleep(NFS_SLEEP)
        stat = os.stat(os.path.join(self.fake_override_repo_location, 'foo'))
        self.assertEqual(stat.st_uid, 501)
        self.assertEqual(stat.st_gid, 20)

    def test_mount_repo_waits_for_restart(self):
        server.add_exports_for_repos([Repo('github.com/app/a')])
        check_and_log_output_and_error(['nfsd', 'restart'], demote=False)
        client._mount_repo(Repo('github.com/app/a'), wait_for_server=True)
        # no errors mean it worked
        client._unmount_repo(Repo('github.com/app/a'))

    def test_mount_repo_doesnt_wait(self):
        server.add_exports_for_repos([Repo('github.com/app/a')])
        check_and_log_output_and_error(['nfsd', 'restart'], demote=False)
        with self.assertRaises(CalledProcessError):
            client._mount_repo(Repo('github.com/app/a'), wait_for_server=False)

    def test_invalid_exports_logged(self):
        with open(constants.EXPORTS_PATH, 'w') as f:
            f.write('bad config')
        self.run_command('bundles activate bundle-a')
        with self.assertRaises(self.CommandError):
            self.run_command('up --no-pull')
