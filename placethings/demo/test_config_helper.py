from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config.base import cfg_helper
from placethings.config.factory import (
    default_device_cfg, default_mapping_cfg, default_task_cfg)
from placethings.demo.base_test import BaseTestCase


log = logging.getLogger()


class TestDefineConfig(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None

        device_data = default_device_cfg.create_default_device_data()
        task_data = default_task_cfg.create_default_task_data()
        mapping_data = default_mapping_cfg.create_default_mapping_data()

        all_cfg = cfg_helper.ConfigHelper(device_data, task_data, mapping_data)

        all_cfg.export_to_file('config_base')
        imported = cfg_helper.ConfigHelper().import_from_file('config_base')
        assert imported.device_data.to_json() == all_cfg.device_data.to_json()
        assert imported.task_data.to_json() == all_cfg.task_data.to_json()
        assert (
            imported.mapping_data.to_json() == all_cfg.mapping_data.to_json())
