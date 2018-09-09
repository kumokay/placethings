from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy
from future.utils import iteritems
import logging

from placethings.config import task_data
from placethings.definition import GtInfo
from placethings.utils import common_utils, graph_utils, json_utils, plot_utils


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


def create_graph(
        mapping, task_links, task_info,
        is_export=False, graph_filename=None, data_filename=None):
    node_info, edge_info = _derive_graph_info(mapping, task_links, task_info)
    graph = graph_utils.gen_graph(task_info, task_links)
    if is_export:
        export_graph(graph, graph_filename)
        export_data(node_info, edge_info, data_filename)
    return graph


def create_default_task_graph(
        is_export=False, graph_filename=None, data_filename=None):
    task_mapping, task_links, task_info = task_data.create_default_task_data()
    return create_graph(
        task_mapping, task_info, task_links,
        is_export, graph_filename, data_filename)


def create_graph_from_file(
        filepath,
        is_export=False, graph_filename=None, data_filename=None):
    task_mapping, task_links, task_info = task_data.import_data(filepath)
    return create_graph(
        task_mapping, task_links, task_info,
        is_export, graph_filename, data_filename)


_DEFAULT_FILE_PATH = 'output/task_graph'


def export_graph(graph, filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH + '.png')
    plot_utils.plot(
        graph,
        with_edge=True,
        which_edge_label=None,
        filepath=filename)


def export_data(node_info, edge_info, filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH + '.json')
    json_utils.export_bundle(
        filename,
        node_info=node_info,
        edge_info=edge_info)
    _node_info, _edge_info = import_data()
    assert _node_info == node_info
    assert _edge_info == edge_info


def import_data(filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH + '.json')
    node_info, edge_info = json_utils.import_bundle(
        filename,
        'node_info',
        'edge_info',
    )
    return node_info, edge_info
