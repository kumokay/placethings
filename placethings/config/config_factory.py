from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config import (
    device_data, nw_device_data, spec_def, init_mapping, default_def,
    task_graph, topo_graph, network_graph)


log = logging.getLogger()


def export_all_config():
    # device data
    device_data.export_data()
    nw_device_data.export_data()
    spec_def.export_data()
    # user defined
    init_mapping.export_data()
    default_def.export_data()
    task_graph.export_data()
    topo_graph.export_data()
    network_graph.export_data()
