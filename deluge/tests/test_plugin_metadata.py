#
# Copyright (C) 2015 Calum Lind <calumlind@gmail.com>
#
# This file is part of Deluge and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

from unittest import mock

from deluge.pluginmanagerbase import PluginManagerBase

from . import common


class TestPluginManagerBase:
    def test_scan_for_plugins(self):
        plugin_dirs_mock = mock.Mock(
            return_value=common.TestPluginManager.get_plugin_dirs(self)
        )
        with mock.patch(
            'deluge.tests.test_plugin_metadata.PluginManagerBase.get_plugin_dirs',
            new=plugin_dirs_mock,
        ):
            pm = PluginManagerBase('core.conf', 'deluge.plugin.core')
            assert 'plugin_resources_test' in pm.available_plugins

    def test_get_plugin_info(self):
        pm = PluginManagerBase('core.conf', 'deluge.plugin.core')
        for p in pm.get_available_plugins():
            for key, value in pm.get_plugin_info(p).items():
                assert isinstance(key, str)
                assert isinstance(value, str)

    def test_get_plugin_info_invalid_name(self):
        pm = PluginManagerBase('core.conf', 'deluge.plugin.core')
        for key, value in pm.get_plugin_info('random').items():
            result = 'not available' if key in ('Name', 'Version') else ''
            assert value == result
