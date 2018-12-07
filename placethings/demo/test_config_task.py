from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config.base import task_cfg
from placethings.config.factory import default_task_cfg
from placethings.demo.base_test import BaseTestCase
from placethings.utils import plot_utils

log = logging.getLogger()

"""
task graph

  capture_image -> detect_object -> send_notification
"""


class TestDefineConfig(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None

        task_data = default_task_cfg.create_default_task_data()

        graph = task_data.to_graph()
        plot_utils.plot(graph, filepath='config_base/task_data.png')

        task_data.export_to_file('config_base/task_data.json')
        task_data_imported = task_cfg.TaskData().import_from_file(
            'config_base/task_data.json')
        assert task_data_imported.to_json() == task_data.to_json()
