from mock import Mock, patch, call
import docker

from nose.tools import nottest

from ....fixtures import premade_app
from ....testcases import DustyTestCase
from dusty.systems.docker.testing_image import (_ensure_base_image, _create_tagged_image, _get_split_volumes, _get_create_container_volumes,
                                                _get_create_container_binds)


@patch('dusty.systems.docker.testing_image.get_expanded_libs_specs')
class TestTestingImages(DustyTestCase):
    def setUp(self):
        super(TestTestingImages, self).setUp()
        app = premade_app()
        app['test'] = {'once': ['npm install']}
        self.specs = {'apps': {'fake-app': app}}

    @patch('dusty.systems.docker.testing_image._testing_spec')
    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_ensure_base_image_image(self, fake_docker_client, fake_testing_spec, fake_expanded_libs):
        fake_docker_client = Mock()
        testing_spec = {'image': 'dusty/image'}
        fake_testing_spec.return_value = testing_spec
        self.assertEquals(_ensure_base_image(testing_spec), 'dusty/image')

    @patch('dusty.systems.docker.testing_image._testing_spec')
    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_ensure_base_image_build(self, fake_docker_client, fake_testing_spec, fake_expanded_libs):
        fake_docker_client.return_value = fake_docker_client
        mock_build = Mock()
        fake_docker_client.build = mock_build
        testing_spec = {'build': '/path/to/docker_file_folder'}
        fake_testing_spec.return_value = testing_spec
        _ensure_base_image(testing_spec)
        mock_build.assert_has_calls([call(path='/path/to/docker_file_folder', tag='dusty_testing_base/image')])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_get_split_volumes_1(self, fake_docker_client, fake_expanded_libs):
        volumes = []
        self.assertEquals([], _get_split_volumes(volumes))

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_get_split_volumes_2(self, fake_docker_client, fake_expanded_libs):
        volumes = ['/persist/repos/gc/a:/gc/a', '/persist/repos/gc/b:/gc/b']
        self.assertEquals(_get_split_volumes(volumes), [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                                                        {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_get_create_container_volumes(self, fake_docker_client, fake_expanded_libs):
        split_volumes = [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                         {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}]
        self.assertEquals(['/gc/a', '/gc/b'], _get_create_container_volumes(split_volumes))

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_get_create_container_binds(self, fake_docker_client, fake_expanded_libs):
        split_volumes = [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                         {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}]
        expected_dict = {'/persist/repos/gc/a': {'bind': '/gc/a', 'ro': False},
                         '/persist/repos/gc/b': {'bind': '/gc/b', 'ro': False}}
        self.assertEquals(expected_dict, _get_create_container_binds(split_volumes))

    @patch('dusty.systems.docker.testing_image.get_volume_mounts')
    @patch('dusty.systems.docker.testing_image._get_test_image_setup_command')
    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image.log_to_client')
    def test_create_tagged_image(self, fake_log_to_client, fake_docker_client, fake_command,
                          fake_volume_mounts, fake_expanded_libs):
        fake_expanded_libs.return_value = self.specs
        command = 'npm install'
        fake_command.return_value = command
        fake_volume_mounts.return_value = []
        fake_docker_client.return_value = fake_docker_client
        fake_docker_client.create_container.return_value = {'Id': '1'}
        fake_docker_client.commit.return_value = {'Id': '2'}
        image_tag = 'dusty/image'
        fake_docker_client.images.return_value = [{'RepoTags': [image_tag]}]
        image_name = 'gcweb_testing_image'
        fake_docker_client.logs.return_value = ['installing a', 'installing b']
        fake_docker_client.wait.return_value = 0
        _create_tagged_image(image_tag, image_name, 'fake-app')
        fake_docker_client.create_container.assert_has_calls([call(image=image_tag,
                                                                   command=command,
                                                                   volumes=[],
                                                                   host_config=docker.utils.create_host_config(binds={}))])
        fake_docker_client.start.assert_has_calls([call(container='1')])
        fake_docker_client.logs.assert_has_calls([call('1', stdout=True, stderr=True, stream=True)])
        fake_docker_client.commit.assert_has_calls([call(container='1')])
        fake_docker_client.tag.assert_has_calls([call(image='2', repository=image_name, force=True)])
        fake_log_to_client.assert_has_calls([call('Running commands to create new image:'),call('installing a'), call('installing b')])
