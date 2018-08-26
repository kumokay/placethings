from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import random

import networkx as nx

from placethings.definition import GnInfo
from placethings.utils import Unit


log = logging.getLogger()


class TopoGraph(object):

    _DEFAULT_DENSITY = 0.3
    _DEFAULT_LATENCY = Unit.ms(20)
    _DEFAULT_BANDWIDTH = Unit.mbyte(300)
    # default nodes in the topology if not present in input arguments
    _DEFAULT_N_SWITCH = 10
    _DEFAULT_N_DEVICE = 5
    _DEFAULT_N_SOURCE = 3
    _DEFAULT_N_DESTINATION = 1
    _DEFAULT_PREFIX_SWITCH = 'sw'
    _DEFAULT_PREFIX_DEVICE = 'dv'
    _DEFAULT_PREFIX_SOURCE = 'src'
    _DEFAULT_PREFIX_DESTINATION = 'dst'

    @classmethod
    def create_default_switch_list(cls, n_switch=None):
        # expose this function to network graph
        if not n_switch:
            n_switch = cls._DEFAULT_N_SWITCH
        return cls._create_node_list(n_switch, cls._DEFAULT_PREFIX_SWITCH)

    @classmethod
    def _create_node_list(cls, n_node, node_prefix):
        return ['{}.{}'.format(node_prefix, i) for i in range(n_node)]

    @classmethod
    def _add_random_link(cls, graph, src, dst):
        attr = {
            GnInfo.BANDWIDTH: cls._DEFAULT_BANDWIDTH * random.random(),
            GnInfo.LATENCY: cls._DEFAULT_LATENCY * random.random(),
        }
        graph.add_edge(src, dst, **attr)

    @classmethod
    def create_default_topo(
            cls,
            switch_list=None,
            device_list=None,
            source_list=None,
            dst_list=None):
        """
        Randomly deploy devices in a newtork consists of randomly connected
        switches.

        Args:
            switch_list (list): a list of APs, routers, switchs, etc
            device_list (list): a list of devices
            source_list (list): a list of data sources
            dst_list (list): a list of actuators
        Returns:
            topology (networkx.DiGraph)
        """
        if not switch_list:
            switch_list = cls._create_node_list(
                cls._DEFAULT_N_SWITCH, cls._DEFAULT_PREFIX_SWITCH)
        if not device_list:
            device_list = cls._create_node_list(
                cls._DEFAULT_N_DEVICE, cls._DEFAULT_PREFIX_DEVICE)
        if not source_list:
            source_list = cls._create_node_list(
                cls._DEFAULT_N_SOURCE, cls._DEFAULT_PREFIX_SOURCE)
        if not dst_list:
            dst_list = cls._create_node_list(
                cls._DEFAULT_N_DESTINATION, cls._DEFAULT_PREFIX_DESTINATION)

        graph = nx.DiGraph()
        graph.add_nodes_from(switch_list)
        n_edge_per_switch = int(round(cls._DEFAULT_DENSITY * len(switch_list)))
        for s1 in switch_list:
            for s2 in random.sample(switch_list, n_edge_per_switch):
                if s1 == s2:
                    continue
                cls._add_random_link(graph, s1, s2)
                cls._add_random_link(graph, s2, s1)
        client_list = device_list + source_list +dst_list
        graph.add_nodes_from(client_list)
        for node in client_list:
            # connect device to a random selected switch
            [switch] = random.sample(switch_list, 1)
            # randomly assign bandwidth and latency
            cls._add_random_link(graph, node, switch)
            cls._add_random_link(graph, switch, node)
        return graph
