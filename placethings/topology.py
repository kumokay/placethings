from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import random
from future.utils import iteritems

import networkx as nx
from matplotlib import pyplot as plt


log = logging.getLogger()


class Topology(object):

    _DEFAULT_LINK_SPEED_MS = 10
    _DEFAULT_DEVICE_INFO = {
        't2.micro': {
            'task_capacity': 10,
            'cost_per_hour': 0.0116,
        },
        'g3.4xlarge': {
            'task_capacity': 100,
            'cost_per_hour': 1.14,
        },
        'nuc': {
            'task_capacity': 10,
            'cost_per_hour': 0,
        },
    }
    _DEFAULT_DEVICE_AVALIBILITY = {
        't2.micro': 20,
        'g3.4xlarge': 2,
        'nuc': 10,
    }
    _DEFAULT_LINK_DENSITY = 0.7

    @classmethod
    def _link_two_hosts(cls, topo, h1, h2):

        def _rand_link_speed():
            return cls._DEFAULT_LINK_SPEED_MS * random.random()

        # asymmetric link speed
        topo.add_edge(
            h1,
            h2,
            latency=_rand_link_speed(),
        )
        topo.add_edge(
            h2,
            h1,
            latency=_rand_link_speed(),
        )

    @classmethod
    def _add_links(cls, topo, link_density):
        """
        Args:
            topo (networkx.DiGraph): a graph with nodes but no edges
            link_density (float): possibility of having links between hosts
        Returns:
            topo (networkx.Digraph): network topology with links
        """
        host_list = topo.nodes()
        n_link_per_host = int(round(len(host_list) * link_density))  # ceil(x)
        for h1 in topo.nodes():
            for h2 in random.sample(host_list, n_link_per_host):
                if h1 == h2:
                    continue
                cls._link_two_hosts(topo, h1, h2)
            assert len(topo.edges(h1)) > 0, 'host {} has no edges'.format(h1)
        return topo

    @staticmethod
    def _add_hosts(topo, device_info, device_availability):
        """
        Args:
            topo (networkx.DiGraph): an empty graph
            device_availability (dict): how many devices are available, e.g.
                device_availability = {
                    't2.micro': 20,
                    'g3.4xlarge': 2,
                    'nuc': 10,
                }
            device_info (dict): device information, e.g.
                device_info = {
                    't2.micro': {
                        'task_capacity': 10,
                        'cost_per_hour': 0.0116,
                    }
                    'g3.4xlarge': {
                        'task_capacity': 100,
                        'cost_per_hour': 1.14,
                    }
                    'nuc': {
                        'task_capacity': 10,
                        'cost_per_hour': 0,
                    }
                }
        Returns:
            topo (networkx.DiGraph): graph with nodes but without edges
        """
        def _gen_device_id_str(device_name, ith_device):
            return '{}_{}'.format(device_name, ith_device)

        for device_name, n_device in iteritems(device_availability):
            device_attr = device_info.get(device_name, None)
            if not device_attr:
                log.warning('no device info for {}'.format(device_name))
                continue
            for i in range(n_device):
                topo.add_node(
                    _gen_device_id_str(device_name, i),
                    **device_attr)
        return topo

    @classmethod
    def create(cls, device_info, device_availability, link_density):
        topo = nx.DiGraph()
        topo = cls._add_hosts(topo, device_info, device_availability)
        topo = cls._add_links(topo, link_density)
        return topo

    @classmethod
    def create_default(cls):
        log.info('create default topo')
        device_info = cls._DEFAULT_DEVICE_INFO
        device_availability = cls._DEFAULT_DEVICE_AVALIBILITY
        link_density = cls._DEFAULT_LINK_DENSITY

        topo = nx.DiGraph()
        topo = cls._add_hosts(topo, device_info, device_availability)
        topo = cls._add_links(topo, link_density)
        return topo

    @staticmethod
    def plot(topo):
        nx.draw_networkx(
            topo,
            pos=nx.spring_layout(topo),
            arrows=False,
            with_labels=True,
        )
        plt.show(topo)
