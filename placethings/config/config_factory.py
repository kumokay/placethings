from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config import (
    device_data, nw_device_data,
    init_mapping, task_graph, topo_graph, network_graph)
from placethings.utils import common_utils


log = logging.getLogger()


def export_all_config():
    # device data
    device_data.export_data()
    nw_device_data.export_data()
    # user defined
    init_mapping.export_data()
    task_graph.export_data()
    topo_graph.export_data()
    network_graph.export_data()


def import_all_config(config_name):
    # device data
    filename = 'device_data.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    device_spec, device_inventory = device_data.import_data(filepath)
    filename = 'nw_device_data.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    nw_device_spec, nw_device_inventory = nw_device_data.import_data(filepath)
    # user defined
    filename = 'default_map.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    init_map = init_mapping.import_data(filepath)
    filename = 'task_graph.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    Gt_node, Gt_edge = task_graph.import_data(filename)
    filename = 'topo_graph.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    Gn_node, Gn_edge = topo_graph.impoort_data(filename)
    filename = 'network_graph.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    Gd_node, Gd_edge = network_graph.import_data(filename)
    return (
        device_spec, device_inventory, nw_device_spec, nw_device_inventory,
        init_map, Gt_node, Gt_edge, Gn_node, Gn_edge, Gd_node, Gd_edge)
