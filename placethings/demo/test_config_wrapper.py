from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings import ilp_solver
from placethings.config import device_data, nw_device_data
from placethings.definition import GnInfo, Unit
from placethings.graph_gen import graph_factory, device_graph
from placethings.config.config_factory import FileHelper
from placethings.demo.base_test import BaseTestCase


log = logging.getLogger()

_DEFAULT_CONFIG = 'config_default'


class TestConfigWrapper(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None
