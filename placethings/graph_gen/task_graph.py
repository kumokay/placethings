from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy
from future.utils import iteritems
import logging

from placethings.config import task_data
from placethings.definition import GtInfo
from placethings.graph_gen.graph_utils import GraphGen, FileHelper


log = logging.getLogger()


def _derive_node_info(task_mapping, task_info):
    node_info = {}
    for task_name, data in iteritems(task_info):
        node_info[task_name] = {
            GtInfo.LATENCY_INFO: deepcopy(data[GtInfo.LATENCY_INFO]),
            GtInfo.RESRC_RQMT: deepcopy(data[GtInfo.RESRC_RQMT]),
            GtInfo.DEVICE: task_mapping[task_name],
        }
    return node_info


def _derive_edge_info(task_links):
    edge_info = task_links
    # nothing to derive
    return edge_info


def _derive_graph_info(task_mapping, task_links, task_info):
    node_info = _derive_node_info(task_mapping, task_info)
    edge_info = _derive_edge_info(task_links)
    return node_info, edge_info


def create_graph(mapping, task_links, task_info, is_export=False):
    node_info, edge_info = _derive_graph_info(mapping, task_links, task_info)
    graph = GraphGen.create(node_info, edge_info)
    if is_export:
        FileHelper.export_graph(graph, 'task_graph')
        FileHelper.export_data(node_info, edge_info, 'task_graph')
    return graph


def create_default_graph(is_export=False):
    task_mapping, task_links, task_info = task_data.create_default_task_data()
    return create_graph(task_mapping, task_info, task_links, is_export)


def create_graph_from_file(filepath, is_export=False):
    task_mapping, task_links, task_info = task_data.import_data(filepath)
    return create_graph(task_mapping, task_links, task_info, is_export)
