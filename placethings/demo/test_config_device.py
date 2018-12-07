from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config.base import device_cfg
from placethings.config.factory import default_device_cfg
from placethings.demo.base_test import BaseTestCase
from placethings.utils import plot_utils

log = logging.getLogger()


class TestDefineNwConfig(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None

        device_data = default_device_cfg.create_default_network_device_data()

        graph = device_data.to_graph()
        plot_utils.plot(graph, filepath='config_base/nw_device_data.png')

        device_data.export_to_file('config_base/nw_device_data.json')
        device_data_imported = device_cfg.DeviceData().import_from_file(
            'config_base/nw_device_data.json')
        assert device_data_imported.to_json() == device_data.to_json()


class TestDefineConfig(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None

        device_data = default_device_cfg.create_default_device_data()

        graph = device_data.to_graph()
        plot_utils.plot(graph, filepath='config_base/all_device_data.png')

        device_data.export_to_file('config_base/all_device_data.json')
        device_data_imported = device_cfg.DeviceData().import_from_file(
            'config_base/all_device_data.json')
        assert device_data_imported.to_json() == device_data.to_json()
