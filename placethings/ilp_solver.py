from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import pulp

from placethings.topology import Topology


log = logging.getLogger()

INT_MAX = 2147483647


class Problems:

    @staticmethod
    def _get_path_length(graph, node_list):
        permutations = pulp.permutation(node_list, len(node_list))
        min_path = INT_MAX
        for p_tuple in permutations:
            path_len = 0
            prev_node = p_tuple[0]
            for node in p_tuple[1:]:
                edge_data = graph.get_edge_data(prev_node, node)
                if edge_data is None:
                    return INT_MAX
                path_len += edge_data['latency']
                prev_node = node
            if path_len < min_path:
                path_len = path_len
        return path_len

    @classmethod
    def place_things(cls):

        topo = Topology.create_default()
        device_list = list(topo.nodes())

        n_task = 10

        # create a binary variable to state that a device is used
        device_state = pulp.LpVariable.dicts(
            'device_state',
            device_list,
            lowBound=0,
            upBound=1,
            cat=pulp.LpInteger)

        # define the problem and add constrains
        n_task = 10
        modle = pulp.LpProblem("placething model", pulp.LpMinimize)

        constrain = sum(device_state[name] for name in device_list) == n_task
        msg = 'n_device picked == n_task'
        modle += constrain, msg

        candidates = [name for name in device_state if device_state[name] == 1]
        constrain = cls._get_path_length(topo, candidates)
        msg = 'find shortest path'
        modle += constrain, msg

        # TODO: add more constrains
