from mock import patch, call, Mock

from dusty.commands import assets, bundles

from ...testcases import DustyTestCase

@patch('dusty.commands.assets.initialize_docker_vm')
@patch('dusty.commands.assets.asset_is_set')
class TestAssetsCommands(DustyTestCase):
    def assertAppOrLibAssetListed(self, asset_name, path):
        self.assertTrue(any([asset_name in line and path in line
            for line in self.last_client_output.splitlines()]))

    def assertAssetListed(self, asset_name, used_by, required_by):
        self.assertTrue(any([asset_name in line and assets._get_string_of_set(used_by) in line and assets._get_string_of_set(required_by) in line
            for line in self.last_client_output.splitlines()]))

    def test_list_by_app(self, fake_asset_is_set, *args):
        fake_asset_is_set.return_value = True
        assets.list_by_app_or_lib('app-a')
        self.assertAppOrLibAssetListed('required_asset', 'required_path')
        self.assertAppOrLibAssetListed('optional_asset', 'optional_path')

    def test_list_by_lib(self, fake_asset_is_set, *args):
        fake_asset_is_set.return_value = False
        assets.list_by_app_or_lib('lib-a')
        self.assertAppOrLibAssetListed('required_lib_asset', 'required_path')
        self.assertAppOrLibAssetListed('optional_lib_asset', 'optional_path')

    def test_list(self, fake_asset_is_set, *args):
        fake_asset_is_set.return_value = True
        bundles.activate_bundle(['bundle-a'])
        assets.list_all()
        self.assertAssetListed('required_asset', ['app-a'], ['app-a'])
        self.assertAssetListed('optional_asset', ['app-a'], [])
        self.assertAssetListed('required_lib_asset', ['lib-a'], ['lib-a'])
        self.assertAssetListed('optional_lib_asset', ['lib-a'], [])
        self.assertAssetListed('common_asset', ['app-a', 'lib-a'], ['app-a'])
