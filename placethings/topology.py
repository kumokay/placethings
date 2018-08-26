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

    _DEFAULT_N_SWITCH = 10
    _DEFAULT_N_DEVICE = 5
    _DEFAULT_DENSITY = 0.3
    _DEFAULT_LATENCY = Unit.ms(20)
    _DEFAULT_BANDWIDTH = Unit.mbyte(300)
    _DEFAULT_SWITCH_PREFIX = 'sw'
    _DEFAULT_DEVICE_PREFIX = 'dv'

    @classmethod
    def create_default_switch_list(cls, n_switch=None):
        if not n_switch:
            n_switch = cls._DEFAULT_N_SWITCH
        switch_list = [
            '{}.{}'.format(cls._DEFAULT_SWITCH_PREFIX, i)
            for i in range(n_switch)]
        return switch_list

    @classmethod
    def _create_default_device_list(cls, n_device=None):
        if not n_device:
            n_device = cls._DEFAULT_N_DEVICE
        device_list = [
            '{}.{}'.format(cls._DEFAULT_DEVICE_PREFIX, i)
            for i in range(n_device)]
        return device_list

    @classmethod
    def _add_random_link(cls, graph, src, dst):
        attr = {
            GnInfo.BANDWIDTH: cls._DEFAULT_BANDWIDTH * random.random(),
            GnInfo.LATENCY: cls._DEFAULT_LATENCY * random.random(),
        }
        graph.add_edge(src, dst, **attr)

    @classmethod
    def create_default_topo(cls, switch_list=None, device_list=None):
        """
        Randomly deploy devices in a newtork consists of randomly connected
        switches.

        Args:
            switch_list (list): a list of APs, routers, switchs, etc
            device_list (list): a list of devices
        Returns:
            topology (networkx.DiGraph)
        """
        if not switch_list:
            switch_list = cls.create_default_switch_list()
        if not device_list:
            device_list = cls._create_default_device_list()
        graph = nx.DiGraph()
        graph.add_nodes_from(switch_list)
        n_edge_per_switch = int(round(cls._DEFAULT_DENSITY * len(switch_list)))
        for s1 in switch_list:
            for s2 in random.sample(switch_list, n_edge_per_switch):
                if s1 == s2:
                    continue
                cls._add_random_link(graph, s1, s2)
                cls._add_random_link(graph, s2, s1)
        graph.add_nodes_from(device_list)
        for device in device_list:
            # connect device to a random selected switch
            [switch] = random.sample(switch_list, 1)
            # randomly assign bandwidth and latency
            cls._add_random_link(graph, device, switch)
            cls._add_random_link(graph, switch, device)
        return graph
