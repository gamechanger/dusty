from mock import Mock, patch, call
import docker

from ....testcases import DustyTestCase
from dusty.systems.docker.testing_image import (_ensure_testing_spec_base_image, _make_installed_requirements_image,
                                                _make_installed_testing_image, _get_split_volumes, _get_create_container_volumes,
                                                _get_create_container_binds)
from dusty.systems.docker.testing_image import ensure_image_exists

class TestTestingImages(DustyTestCase):
    def test_ensure_testing_spec_base_image_wrong_arguments_1(self):
        testing_spec = {}
        with self.assertRaises(RuntimeError):
            _ensure_testing_spec_base_image(testing_spec)

    def test_ensure_testing_spec_base_image_wrong_arguments_2(self):
        testing_spec = {'image': 'dusty/image', 'build': '/path/to/docker_file_folder'}
        with self.assertRaises(RuntimeError):
            _ensure_testing_spec_base_image(testing_spec)

    def test_ensure_testing_spec_base_image_image(self):
        testing_spec = {'image': 'dusty/image'}
        self.assertEquals(_ensure_testing_spec_base_image(testing_spec), 'dusty/image')

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_ensure_testing_spec_base_image_build(self, fake_get_docker_client):
        mock_docker_client = Mock()
        mock_build = Mock()
        fake_get_docker_client.return_value = mock_docker_client
        mock_docker_client.build = mock_build
        testing_spec = {'build': '/path/to/docker_file_folder'}
        _ensure_testing_spec_base_image(testing_spec)
        fake_get_docker_client.assert_has_calls([call()])
        mock_build.assert_has_calls([call(path='/path/to/docker_file_folder', tag='dusty_testing_base/image')])

    def test_get_split_volumes_1(self):
        volumes = []
        self.assertEquals([], _get_split_volumes(volumes))

    def test_get_split_volumes_2(self):
        volumes = ['/persist/repos/gc/a:/gc/a', '/persist/repos/gc/b:/gc/b']
        self.assertEquals(_get_split_volumes(volumes), [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                                                        {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}])

    def test_get_create_container_volumes(self):
        split_volumes = [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                         {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}]
        self.assertEquals(['/gc/a', '/gc/b'], _get_create_container_volumes(split_volumes))

    def test_get_create_container_binds(self):
        split_volumes = [{'host_location': '/persist/repos/gc/a', 'container_location': '/gc/a'},
                         {'host_location': '/persist/repos/gc/b', 'container_location': '/gc/b'}]
        expected_dict = {'/persist/repos/gc/a': {'bind': '/gc/a', 'ro': False},
                         '/persist/repos/gc/b': {'bind': '/gc/b', 'ro': False}}
        self.assertEquals(expected_dict, _get_create_container_binds(split_volumes))

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_make_installed_requirements_image_1(self, fake_get_docker_client):
        mock_docker_client = Mock()
        fake_get_docker_client.return_value = mock_docker_client
        mock_docker_client.create_container.return_value = {'Id': '1'}
        mock_docker_client.commit.return_value = {'Id': '2'}
        image_tag = 'dusty/image'
        command = 'npm install'
        image_name = 'gcweb_testing_image'
        _make_installed_requirements_image(image_tag, command, image_name)
        mock_docker_client.create_container.assert_has_calls([call(image=image_tag,
                                                                   command=command,
                                                                   volumes=[],
                                                                   host_config=docker.utils.create_host_config(binds={}))])
        mock_docker_client.start.assert_has_calls([call(container='1')])
        mock_docker_client.commit.assert_has_calls([call(container='1')])
        mock_docker_client.tag.assert_has_calls([call(image='2', repository=image_name, force=True)])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_make_installed_requirements_image_2(self, fake_get_docker_client):
        mock_docker_client = Mock()
        fake_get_docker_client.return_value = mock_docker_client
        mock_docker_client.create_container.return_value = {'Id': '1'}
        mock_docker_client.commit.return_value = {'Id': '2'}
        image_tag = 'dusty/image'
        command = 'npm install'
        image_name = 'gcweb_testing_image'
        _make_installed_requirements_image(image_tag, command, image_name, volumes=['os/path:container/path'])
        mock_docker_client.create_container.assert_has_calls([call(image=image_tag,
                                                                   command=command,
                                                                   volumes=['container/path'],
                                                                   host_config=docker.utils.create_host_config(binds={
                                                                        'os/path': {'bind': 'container/path',
                                                                                    'ro': False}
                                                                    }))])
        mock_docker_client.start.assert_has_calls([call(container='1')])
        mock_docker_client.wait.assert_has_calls([call(container='1')])
        mock_docker_client.commit.assert_has_calls([call(container='1')])
        mock_docker_client.tag.assert_has_calls([call(image='2', repository=image_name, force=True)])

    @patch('dusty.systems.docker.testing_image._ensure_testing_spec_base_image')
    @patch('dusty.systems.docker.testing_image._make_installed_requirements_image')
    def test_make_installed_testing_image(self, fake_make_installed_image, fake_ensure_base_image):
        testing_spec = {'once': 'npm install'}
        new_image_name = 'dusty/image'
        fake_ensure_base_image.return_value = 'dusty_testing/image'
        _make_installed_testing_image(testing_spec, new_image_name, volumes=['os/path:container:path'])
        fake_ensure_base_image.assert_has_calls([call(testing_spec)])
        fake_make_installed_image.assert_has_calls([call('dusty_testing/image', 'npm install', new_image_name, volumes=['os/path:container:path'])])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._make_installed_testing_image')
    def test_ensure_image_exists_no_force_1(self, fake_make_installed_image, fake_get_docker_client):
        fake_docker_client = Mock()
        fake_get_docker_client.return_value = fake_docker_client
        fake_docker_client.images.return_value = []
        testing_spec = {'once': 'npm install'}
        new_image_name = 'dusty/image'
        ensure_image_exists(testing_spec, new_image_name)
        fake_make_installed_image.assert_has_calls([call(testing_spec, new_image_name, volumes=[])])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._make_installed_testing_image')
    def test_ensure_image_exists_no_force_2(self, fake_make_installed_image, fake_get_docker_client):
        fake_docker_client = Mock()
        fake_get_docker_client.return_value = fake_docker_client
        fake_docker_client.images.return_value = []
        testing_spec = {'once': 'npm install'}
        new_image_name = 'dusty/image'
        ensure_image_exists(testing_spec, new_image_name, volumes=['os/path:container:path'])
        fake_make_installed_image.assert_has_calls([call(testing_spec, new_image_name, volumes=['os/path:container:path'])])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._make_installed_testing_image')
    def test_ensure_image_exists_no_force_3(self, fake_make_installed_image, fake_get_docker_client):
        fake_docker_client = Mock()
        fake_get_docker_client.return_value = fake_docker_client
        fake_docker_client.images.return_value = [{'RepoTags': ['dusty', 'dusty/dog']},
                                                  {'RepoTags': ['dusty/images', 'dusty/image']}]
        testing_spec = {'once': 'npm install'}
        new_image_name = 'dusty/image'
        ensure_image_exists(testing_spec, new_image_name)
        fake_make_installed_image.assert_has_calls([])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    @patch('dusty.systems.docker.testing_image._make_installed_testing_image')
    def test_ensure_image_exists_force(self, fake_make_installed_image, fake_get_docker_client):
        fake_docker_client = Mock()
        fake_get_docker_client.return_value = fake_docker_client
        fake_docker_client.images.return_value = [{'RepoTags': ['dusty', 'dusty/dog']},
                                                  {'RepoTags': ['dusty/images', 'dusty/image']}]
        testing_spec = {'once': 'npm install'}
        new_image_name = 'dusty/image'
        ensure_image_exists(testing_spec, new_image_name, volumes=['os/path:container:path'],force_recreate=True)
        fake_make_installed_image.assert_has_calls([call(testing_spec, new_image_name, volumes=['os/path:container:path'])])
