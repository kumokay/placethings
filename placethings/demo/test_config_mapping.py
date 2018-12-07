from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config.base import mapping_cfg
from placethings.config.factory import default_mapping_cfg
from placethings.demo.base_test import BaseTestCase

log = logging.getLogger()

"""
task graph

  capture_image -> detect_object -> send_notification
"""


class TestDefineConfig(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None

        mapping_data = default_mapping_cfg.create_default_mapping_data()

        mapping_data.export_to_file('config_base/mapping_data.json')
        mapping_data_imported = mapping_cfg.MappingData().import_from_file(
            'config_base/mapping_data.json')
        assert mapping_data_imported.to_json() == mapping_data.to_json()
