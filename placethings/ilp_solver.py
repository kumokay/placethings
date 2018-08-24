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
    def place_things(cls, task_graph):

        topo = Topology.create_default()
        device_list = list(topo.nodes())

        # define the problem and add constrains
        modle = pulp.LpProblem("placething model", pulp.LpMinimize)

        n_task = len(task_graph)
        combination_list = pulp.combination(device_list, n_task)

        # define variables
        var_task_exec_time = [
            pulp.LpVariable(node['name'], lowBound=MIN, upBound=MAX, cat=pulp.LpFloat)
            for node in task_graph.nodes()]

        var_link_latency = [
            pulp.LpVariable(edge['name'], lowBound=MIN, upBound=MAX, cat=pulp.LpFloat)
            for edge in task_graph.edges()]

        # task
        task_attr = defaultdict()
        for node in task_graph.nodes():
            name = node['name']
            task_attr[node['name']] = {
                'device_type': pulp.LpVariable('d_{}'.format(name), cat=pulp.LpInterger),
                'hardware': pulp.LpVariable('h_{}'.format(name), cat=pulp.LpInterger),
                'sensor': pulp.LpVariable('s_{}'.format(name), cat=pulp.LpInterger),
            }

        # define objective
        constrain = sum(var_link_latency) + sum(var_task_exec_time)
        msg = 'minimize total latency'
        modle += constrain, msg

        # define constrains
        for node in task_graph.nodes():
            # TODO: find intervals from a list [1,2,3 5,7,8]
            intervals = find_intervals(node['device_type'])

                constrain = task_attr[node['name']]['device_type'] <= type
                msg = 'device type must in {}, {}'.format(TYPE_A, TYPE_B)


        # TODO: add more constrains
