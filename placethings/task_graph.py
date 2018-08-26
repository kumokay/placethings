from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from future.utils import iteritems
import networkx as nx
from matplotlib import pyplot as plt

from placethings.definition import Device, Flavor, GtInfo, Hardware
from placethings.utils import Unit


log = logging.getLogger()


class TaskGraph(object):

    @classmethod
    def create(
            cls,
            src_list,
            dst_list,
            task_info,
            edge_info):
        """
        Args:
            src_list (list)
            dst_list (list)
            task_info (dict)
            edge_info (dict)
        Returns:
            graph (networkx.DiGraph)

        """
        # currently only support multi-source, single destination
        assert len(src_list) > 0
        assert len(dst_list) == 1
        graph = nx.DiGraph()
        # create graph from input data
        cls._add_nodes(graph, src_list, dst_list, task_info)
        cls._add_edges(graph, edge_info)
        # derive extra information from the input data and stored in the graph
        cls._derive_data(graph, task_info)
        return graph

    @staticmethod
    def _add_nodes(graph, src_list, dst_list, task_info):
        for src in src_list:
            graph.add_node(src)
        for dst in dst_list:
            graph.add_node(dst)
        for name, attr in iteritems(task_info):
            graph.add_node(name, **attr)

    @staticmethod
    def _add_edges(graph, edge_info):
        for edge_str, attr in iteritems(edge_info):
            src_node, dst_node = edge_str.split(' -> ')
            assert src_node in graph.nodes()
            assert dst_node in graph.nodes()
            graph.add_edge(src_node, dst_node, **attr)

    @staticmethod
    def _derive_data(graph, task_info):
        for task in task_info:
            ingress_traffic = sum(
                [graph[src][dst][GtInfo.TRAFFIC]
                    for (src, dst) in graph.edges() if dst == task])
            egress_traffic = sum(
                [graph[src][dst][GtInfo.TRAFFIC]
                    for edge in graph.edges() if src == task])
            build_rqmt_info = graph.node[task][GtInfo.RESOURCE_RQMT]
            for _build, rqmt in iteritems(build_rqmt_info):
                rqmt[Hardware.NIC_INGRESS] = ingress_traffic
                rqmt[Hardware.NIC_EGRESS] = egress_traffic

    @classmethod
    def create_default_graph(cls):
        src_list, dst_list, task_info, edge_info = cls.create_default_data()
        return cls.create(src_list, dst_list, task_info, edge_info)

    @classmethod
    def create_default_data(cls):
        log.info('create default task graph')
        src_list = ['sensor_thermal1', 'sensor_thermal2', 'sensor_camera']
        dst_list = ['accuator_broadcastSystem']
        task_info = {
            'task_getAvgTemperature': {
                GtInfo.LATENCY_INFO: {
                    Device.T3_MICRO: Unit.ms(15),
                    Device.T3_LARGE: Unit.ms(10),
                    Device.P3_2XLARGE: Unit.ms(5),
                },
                GtInfo.RESOURCE_RQMT: {
                    Flavor.CPU: {
                        Hardware.RAM: Unit.mbyte(1),
                        Hardware.HD: Unit.kbyte(3),
                        Hardware.GPU: Unit.percentage(0),
                        Hardware.CPU: Unit.percentage(5),
                    }
                },
            },
            'task_findObject': {
                GtInfo.LATENCY_INFO: {
                    Device.T3_MICRO: Unit.ms(1),
                    Device.T3_LARGE: Unit.ms(1),
                    Device.P3_2XLARGE: Unit.ms(1),
                },
                GtInfo.RESOURCE_RQMT: {
                    Flavor.GPU: {
                        Hardware.RAM: Unit.gbyte(4),
                        Hardware.HD: Unit.mbyte(500),
                        Hardware.GPU: Unit.percentage(60),
                        Hardware.CPU: Unit.percentage(5),
                    },
                    Flavor.CPU: {
                        Hardware.RAM: Unit.gbyte(1),
                        Hardware.HD: Unit.mbyte(300),
                        Hardware.GPU: Unit.percentage(0),
                        Hardware.CPU: Unit.percentage(80),
                    },
                },
            },
            'task_checkAbnormalEvent': {
                GtInfo.LATENCY_INFO: {
                    Device.T3_MICRO: Unit.ms(5000),
                    Device.T3_LARGE: Unit.ms(2500),
                    Device.P3_2XLARGE: Unit.ms(1000),
                },
                GtInfo.RESOURCE_RQMT: {
                    Flavor.CPU: {
                        Hardware.RAM: Unit.mbyte(1),
                        Hardware.HD: Unit.kbyte(3),
                        Hardware.GPU: Unit.percentage(0),
                        Hardware.CPU: Unit.percentage(5),
                    },
                },
            },
            'task_sentNotificatoin': {
                GtInfo.LATENCY_INFO: {
                    Device.T3_MICRO: Unit.ms(1),
                    Device.T3_LARGE: Unit.ms(1),
                    Device.P3_2XLARGE: Unit.ms(1),
                },
                GtInfo.RESOURCE_RQMT: {
                    Flavor.CPU: {
                        Hardware.RAM: Unit.mbyte(1),
                        Hardware.HD: Unit.kbyte(3),
                        Hardware.GPU: Unit.percentage(0),
                        Hardware.CPU: Unit.percentage(5),
                    },
                },
            },
        }
        edge_info = {
            'sensor_thermal1 -> task_getAvgTemperature': {
                GtInfo.TRAFFIC: Unit.kbyte(1),
            },
            'sensor_thermal2 -> task_getAvgTemperature': {
                GtInfo.TRAFFIC: Unit.kbyte(1),
            },
            'sensor_camera -> task_findObject': {
                GtInfo.TRAFFIC: Unit.mbyte(10),
            },
            'task_getAvgTemperature -> task_checkAbnormalEvent': {
                GtInfo.TRAFFIC: Unit.byte(1),
            },
            'task_findObject -> task_checkAbnormalEvent': {
                GtInfo.TRAFFIC: Unit.byte(20),
            },
            'task_checkAbnormalEvent -> task_sentNotificatoin': {
                GtInfo.TRAFFIC: Unit.byte(1),
            },
            'task_sentNotificatoin -> accuator_broadcastSystem': {
                GtInfo.TRAFFIC: Unit.byte(1),
            },
        }
        return src_list, dst_list, task_info, edge_info

    @staticmethod
    def plot(graph):
        nx.draw_networkx(
            graph,
            pos=nx.spring_layout(graph),
            arrows=False,
            with_labels=True,
        )
        plt.show(graph)
