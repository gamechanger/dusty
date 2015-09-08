from mock import Mock, patch, call
import docker

from nose.tools import nottest

from ....fixtures import premade_app
from ....testcases import DustyTestCase
from dusty.systems.docker.testing_image import (_ensure_testing_spec_base_image, _make_installed_requirements_image,
                                                _make_installed_testing_image, _get_split_volumes, _get_create_container_volumes,
                                                _get_create_container_binds)
from dusty.systems.docker.testing_image import ensure_test_image

nottest(ensure_test_image) # silly Nose, this isn't a test function

class TestTestingImages(DustyTestCase):
    def setUp(self):
        super(TestTestingImages, self).setUp()
        app = premade_app()
        app['test'] = {'once': ['npm install']}
        self.specs = {'apps': {'fake-app': app}}

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_ensure_testing_spec_base_image_image(self, fake_docker_client):
        fake_docker_client = Mock()
        testing_spec = {'image': 'dusty/image'}
        self.assertEquals(_ensure_testing_spec_base_image(testing_spec), 'dusty/image')

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_ensure_testing_spec_base_image_build(self, fake_docker_client):
        fake_docker_client.return_value = fake_docker_client
        mock_build = Mock()
        fake_docker_client.build = mock_build
        testing_spec = {'build': '/path/to/docker_file_folder'}
        _ensure_testing_spec_base_image(testing_spec)
        mock_build.assert_has_calls([call(path='/path/to/docker_file_folder', tag='dusty_testing_base/image')])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_get_split_volumes_1(self, fake_docker_client):
        volumes = []
        self.assertEquals([], _get_split_volumes(volumes))

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_get_split_volumes_2(self, fake_docker_client):
        volumes = ['/persist/repos/gc/a:/gc/a', '/persist/repos/gc/b:/gc/b']
        self.assertEquals(_get_split_volumes(volumes), [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                                                        {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_get_create_container_volumes(self, fake_docker_client):
        split_volumes = [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                         {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}]
        self.assertEquals(['/gc/a', '/gc/b'], _get_create_container_volumes(split_volumes))

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_get_create_container_binds(self, fake_docker_client):
        split_volumes = [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                         {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}]
        expected_dict = {'/persist/repos/gc/a': {'bind': '/gc/a', 'ro': False},
                         '/persist/repos/gc/b': {'bind': '/gc/b', 'ro': False}}
        self.assertEquals(expected_dict, _get_create_container_binds(split_volumes))

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image.log_to_client')
    def test_make_installed_requirements_image_1(self, fake_log_to_client, fake_docker_client):
        fake_docker_client.return_value = fake_docker_client
        fake_docker_client.create_container.return_value = {'Id': '1'}
        fake_docker_client.commit.return_value = {'Id': '2'}
        image_tag = 'dusty/image'
        fake_docker_client.images.return_value = [{'RepoTags': [image_tag]}]
        command = 'npm install'
        image_name = 'gcweb_testing_image'
        fake_docker_client.logs.return_value = ['installing a', 'installing b']
        fake_docker_client.wait.return_value = 0
        _make_installed_requirements_image(image_tag, command, image_name, [])
        fake_docker_client.create_container.assert_has_calls([call(image=image_tag,
                                                                   command=command,
                                                                   volumes=[],
                                                                   host_config=docker.utils.create_host_config(binds={}))])
        fake_docker_client.start.assert_has_calls([call(container='1')])
        fake_docker_client.logs.assert_has_calls([call('1', stdout=True, stderr=True, stream=True)])
        fake_docker_client.commit.assert_has_calls([call(container='1')])
        fake_docker_client.tag.assert_has_calls([call(image='2', repository=image_name, force=True)])
        fake_log_to_client.assert_has_calls([call('Running commands to create new image:'),call('installing a'), call('installing b')])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image.log_to_client')
    def test_make_installed_requirements_image_2(self, fake_log_to_client, fake_docker_client):
        fake_docker_client.return_value = fake_docker_client
        fake_docker_client.create_container.return_value = {'Id': '1'}
        fake_docker_client.commit.return_value = {'Id': '2'}
        image_tag = 'dusty/image'
        fake_docker_client.images.return_value = [{'RepoTags': [image_tag]}]
        command = 'npm install'
        image_name = 'gcweb_testing_image'
        fake_docker_client.logs.return_value = ['installing a', 'installing b']
        fake_docker_client.wait.return_value = 0
        _make_installed_requirements_image(image_tag, command, image_name, ['os/path:container/path'])
        fake_docker_client.create_container.assert_has_calls([call(image=image_tag,
                                                                   command=command,
                                                                   volumes=['container/path'],
                                                                   host_config=docker.utils.create_host_config(binds={
                                                                        'os/path': {'bind': 'container/path',
                                                                                    'ro': False}
                                                                    }))])
        fake_docker_client.start.assert_has_calls([call(container='1')])
        fake_docker_client.logs.assert_has_calls([call('1', stdout=True, stderr=True, stream=True)])
        fake_docker_client.commit.assert_has_calls([call(container='1')])
        fake_docker_client.tag.assert_has_calls([call(image='2', repository=image_name, force=True)])
        fake_log_to_client.assert_has_calls([call('Running commands to create new image:'),call('installing a'), call('installing b')])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._ensure_testing_spec_base_image')
    @patch('dusty.systems.docker.testing_image._make_installed_requirements_image')
    def test_make_installed_testing_image(self, fake_make_installed_image, fake_ensure_base_image, fake_docker_client):
        fake_docker_client = Mock()
        new_image_name = 'dusty/test_fake-app'
        fake_ensure_base_image.return_value = 'dusty_testing/image'
        _make_installed_testing_image('fake-app', self.specs)
        fake_ensure_base_image.assert_has_calls([call(self.specs['apps']['fake-app']['test'])])
        fake_make_installed_image.assert_has_calls([call('dusty_testing/image',
                                                         'sh /command_files/dusty_command_file_fake-app.sh', new_image_name,
                                                         ['/command_files/fake-app/test:/command_files', '/persist/dusty_assets:/dusty_assets', '/dusty_repos/tmp/fake-repo:/repo'])])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._make_installed_testing_image')
    def test_ensure_test_image_no_force_1(self, fake_make_installed_image, fake_docker_client):
        fake_docker_client.images.return_value = []
        new_image_name = 'dusty/test_fake-app'
        ensure_test_image('fake-app', self.specs, new_image_name)
        fake_make_installed_image.assert_has_calls([call('fake-app', self.specs)])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._make_installed_testing_image')
    def test_ensure_test_image_no_force_2(self, fake_make_installed_image, fake_docker_client):
        fake_docker_client.images.return_value = []
        new_image_name = 'dusty/image'
        ensure_test_image('fake-app', self.specs, new_image_name)
        fake_make_installed_image.assert_has_calls([call('fake-app', self.specs)])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._make_installed_testing_image')
    def test_ensure_test_image_no_force_3(self, fake_make_installed_image, fake_docker_client):
        fake_docker_client.images.return_value = [{'RepoTags': ['dusty', 'dusty/dog']},
                                                  {'RepoTags': ['dusty/images', 'dusty/image']}]
        new_image_name = 'dusty/image'
        ensure_test_image('fake-app', self.specs, new_image_name)
        fake_make_installed_image.assert_has_calls([])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._make_installed_testing_image')
    def test_ensure_test_image_force(self, fake_make_installed_image, fake_docker_client):
        fake_docker_client.images.return_value = [{'RepoTags': ['dusty', 'dusty/dog']},
                                                  {'RepoTags': ['dusty/images', 'dusty/image']}]
        new_image_name = 'dusty/image'
        ensure_test_image('fake-app', self.specs, force_recreate=True)
        fake_make_installed_image.assert_has_calls([call('fake-app', self.specs)])
