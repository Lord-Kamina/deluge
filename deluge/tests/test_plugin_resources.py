#
# Copyright (C) 2024 Gregorio Litenstein <g.litenstein@gmail.com>
#
# This file is part of Deluge and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

import os
from unittest import mock

import deluge.component as component
from deluge.conftest import BaseTestCase
from deluge.core.core import Core
from deluge.core.pluginmanager import PluginManager
from deluge.core.rpcserver import RPCServer
from deluge.plugin_resource_manager import PluginResourceManager

from . import common

common.disable_new_release_check()


class TestPluginResourceManager(BaseTestCase):
    test_plugin_js = b"""/**
 * Script: plugin_resources_test.js
 *     The client-side javascript code for the plugin_resources_test plugin.
 *
 * Copyright:
 *     (C) Gregorio Litenstein 2024 <g.litenstein@gmail.com>
 *
 *     This file is part of plugin_resources_test and is licensed under GNU GPL 3.0, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */

plugin_resources_testPlugin = Ext.extend(Deluge.Plugin, {
    constructor: function(config) {
        config = Ext.apply({
            name: 'plugin_resources_test'
        }, config);
        plugin_resources_testPlugin.superclass.constructor.call(this, config);
    },

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.plugin_resources_testPage());
    }
});
new plugin_resources_testPlugin();
"""

    def set_up(self):
        with mock.patch(
            'deluge.tests.test_plugin_resources.PluginManager',
            new=common.TestPluginManager,
            create=True,
        ):
            self.rpcserver = RPCServer(listen=False)
            self.core: Core = Core()
            self.core.config.config['lsd'] = False
            self.core.config.config['enabled_plugins'] = []
            self.listen_port = 51242
            return component.start()

    def tear_down(self):
        def on_shutdown(result):
            del self.rpcserver
            del self.core

        return component.shutdown().addCallback(on_shutdown)

    async def test_resource_filename(self):
        self.core.pluginmanager.scan_for_plugins()
        await self.core.pluginmanager.enable_plugin('plugin_resources_test')
        js_file_path = PluginResourceManager.resource_filename(
            'deluge_plugin_resources_test', 'data/plugin_resources_test.js'
        )
        assert os.path.isfile(js_file_path)
        with open(js_file_path, 'rb') as readfile:
            contents = readfile.read()
            assert contents == self.test_plugin_js

    async def test_reuse_previously_extracted_file(self):
        def get_js_file():
            js_file = PluginResourceManager.resource_filename(
                'deluge_plugin_resources_test', 'data/plugin_resources_test.js'
            )
            yield js_file

        self.core.pluginmanager.scan_for_plugins()
        await self.core.pluginmanager.enable_plugin('plugin_resources_test')
        js_file_path = ''
        for i in range(5):
            del i
            if not js_file_path:
                js_file_path = next(get_js_file())
            assert next(get_js_file()) == js_file_path and os.path.isfile(js_file_path)

    async def test_update_path_if_file_deleted(self):
        self.core.pluginmanager.scan_for_plugins()
        await self.core.pluginmanager.enable_plugin('plugin_resources_test')
        js_file_path = PluginResourceManager.resource_filename(
            'deluge_plugin_resources_test', 'data/plugin_resources_test.js'
        )
        assert os.path.isfile(js_file_path)
        os.remove(js_file_path)
        assert not os.path.isfile(js_file_path)
        js_file_path_new = PluginResourceManager.resource_filename(
            'deluge_plugin_resources_test', 'data/plugin_resources_test.js'
        )
        assert js_file_path != js_file_path_new and os.path.isfile(js_file_path_new)

    async def test_clean_files_on_disable_plugin(self):
        self.core.pluginmanager.scan_for_plugins()
        await self.core.pluginmanager.enable_plugin('plugin_resources_test')
        js_file_path = PluginResourceManager.resource_filename(
            'deluge_plugin_resources_test', 'data/plugin_resources_test.js'
        )
        assert os.path.isfile(js_file_path)
        await self.core.pluginmanager.disable_plugin('plugin_resources_test')
        assert not os.path.isfile(js_file_path)
