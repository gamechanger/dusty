from mock import Mock, patch, call

from ....testcases import DustyTestCase
from dusty.systems.docker.testing_image import (_ensure_testing_spec_base_image, _make_installed_requirements_image,
                                                _make_installed_testing_image)

class TestTestingImages(DustyTestCase):
    def test_ensure_testing_spec_base_image_wrong_arguments_1(self):
        testing_spec = {}
        with self.assertRaises(RuntimeError):
            _ensure_testing_spec_base_image(testing_spec)

    def test_ensure_testing_spec_base_image_wrong_arguments_2(self):
        testing_spec = {'image': 'gc/image', 'build': '/path/to/docker_file_folder'}
        with self.assertRaises(RuntimeError):
            _ensure_testing_spec_base_image(testing_spec)

    def test_ensure_testing_spec_base_image_image(self):
        testing_spec = {'image': 'gc/image'}
        self.assertEquals(_ensure_testing_spec_base_image(testing_spec), 'gc/image')

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_ensure_testing_spec_base_image_build(self, fake_get_docker_client):
        mock_docker_client = Mock()
        mock_build = Mock()
        fake_get_docker_client.return_value = mock_docker_client
        mock_docker_client.build = mock_build
        testing_spec = {'build': '/path/to/docker_file_folder'}
        _ensure_testing_spec_base_image(testing_spec)
        fake_get_docker_client.assert_has_calls([call()])
        mock_build.assert_has_calls([call(path='/path/to/docker_file_folder', tag='dusty_testing/image')])

    @patch('dusty.systems.docker.testing_image.get_docker_client')
    def test_make_installed_requirements_image(self, fake_get_docker_client):
        mock_docker_client = Mock()
        fake_get_docker_client.return_value = mock_docker_client
        mock_docker_client.create_container.return_value = {'Id': '1'}
        mock_docker_client.commit.return_value = {'Id': '2'}
        image_tag = 'gc/image'
        command = 'npm install'
        image_name = 'gcweb_testing_image'
        _make_installed_requirements_image(image_tag, command, image_name)
        mock_docker_client.create_container.assert_has_calls([call(image=image_tag, command=command)])
        mock_docker_client.start.assert_has_calls([call(container='1')])
        mock_docker_client.commit.assert_has_calls([call(container='1')])
        mock_docker_client.tag.assert_has_calls([call(image='2', repository=image_name, force=True)])
