from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.graph_gen import device_graph, task_graph, topo_graph
from placethings.utils import common_utils


log = logging.getLogger()


def gen_device_graph(config_name, is_export=False):
    filename = 'device_data.json'
    dev_filepath = common_utils.get_config_filepath(config_name, filename)
    filename = 'nw_device_data.json'
    nw_filepath = common_utils.get_config_filepath(config_name, filename)
    Gd = device_graph.create_graph_from_file(
        dev_filepath, nw_filepath, is_export)
    return Gd


def gen_task_graph(config_name, is_export=False):
    filename = 'task_data.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    Gt = task_graph.create_graph_from_file(filepath, is_export)
    return Gt


def gen_topo_graph(config_name, is_export=False):
    filename = 'nw_device_data.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    Gn = topo_graph.create_graph_from_file(filepath, is_export)
    return Gn


def export_all_graph(config_name):
    gen_device_graph(config_name, is_export=True)
    gen_task_graph(config_name, is_export=True)
    gen_topo_graph(config_name, is_export=True)
