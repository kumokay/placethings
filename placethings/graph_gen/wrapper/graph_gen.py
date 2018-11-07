from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from placethings.config.wrapper.config_gen import Config
from placethings.graph_gen import topo_graph, task_graph, device_graph


def create_topo_graph(cfg, is_export):
    assert type(cfg) is Config
    return topo_graph.create_graph(
        cfg.all_nw_device_data.nw_device_spec.data,
        cfg.all_nw_device_data.nw_device_inventory.data,
        cfg.all_nw_device_data.nw_device_links.data,
        is_export=is_export)


def create_device_graph(cfg, is_export):
    assert type(cfg) is Config
    return device_graph.create_graph(
        cfg.all_device_data.device_spec.data,
        cfg.all_device_data.device_inventory.data,
        cfg.all_device_data.device_links.data,
        cfg.all_nw_device_data.nw_device_spec.data,
        cfg.all_nw_device_data.nw_device_inventory.data,
        cfg.all_nw_device_data.nw_device_links.data,
        is_export=is_export)


def create_task_graph(cfg, is_export):
    assert type(cfg) is Config
    return task_graph.create_graph(
        cfg.all_task_data.task_mapping.data,
        cfg.all_task_data.task_links.data,
        cfg.all_task_data.task_info.data,
        is_export=is_export)
