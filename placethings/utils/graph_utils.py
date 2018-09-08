from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from future.utils import iteritems
import networkx as nx


log = logging.getLogger()


def gen_graph(node_info, edge_info):
    """
    Args:
        task_info (dict)
        edge_info (dict)
    Returns:
        graph (networkx.DiGraph)
    """
    graph = nx.DiGraph()
    for name, attr in iteritems(node_info):
        graph.add_node(name, **attr)
    for edge_str, attr in iteritems(edge_info):
        src_node, dst_node = edge_str.split(' -> ')
        assert src_node in graph.nodes()
        assert dst_node in graph.nodes()
        graph.add_edge(src_node, dst_node, **attr)
    return graph
