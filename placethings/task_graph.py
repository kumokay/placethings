from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from future.utils import iteritems
import networkx as nx
from matplotlib import pyplot as plt

from placethings.definition import Device, Flavor, GtInfo, Hardware, Unit
from placethings.utils import json_utils


log = logging.getLogger()


class TaskGraph(object):

    DEVICE_NOT_ASSIGNED = 'unkown'

    @classmethod
    def create(cls, src_map, dst_map, task_info, edge_info):
        """
        Args:
            src_map (dict): mapping of sensing tasks <-> devices
            dst_map (dict): mapping of actuation tasks <-> devices
            task_info (dict)
            edge_info (dict)
        Returns:
            graph (networkx.DiGraph)

        """
        # currently only support multi-source, single destination
        assert len(src_map) > 0
        assert len(dst_map) == 1
        graph = nx.DiGraph()
        # create graph from input data
        cls._add_nodes(graph, src_map, dst_map, task_info)
        cls._add_edges(graph, edge_info)
        # derive extra information from the input data and stored in the graph
        cls._derive_data(graph, task_info)

        # check graph
        for node in graph.nodes():
            if node in src_map:
                assert graph.node[node][GtInfo.DEVICE] == src_map[node]
            elif node in dst_map:
                assert graph.node[node][GtInfo.DEVICE] == dst_map[node]
            else:
                assert graph.node[node][GtInfo.DEVICE] == (
                    cls.DEVICE_NOT_ASSIGNED)
        return graph

    @classmethod
    def _add_nodes(cls, graph, src_map, dst_map, task_info):
        for map in [src_map, dst_map]:
            for task, device in iteritems(map):
                graph.add_node(task, **{GtInfo.DEVICE: device})
        for name, task_attr in iteritems(task_info):
            attr = {GtInfo.DEVICE: cls.DEVICE_NOT_ASSIGNED}
            attr.update(task_attr)
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
            build_rqmt_info = graph.node[task][GtInfo.RESRC_RQMT]
            for _build, rqmt in iteritems(build_rqmt_info):
                rqmt[Hardware.NIC_INGRESS] = ingress_traffic
                rqmt[Hardware.NIC_EGRESS] = egress_traffic

    @classmethod
    def create_default_graph(cls):
        src_map, dst_map, task_info, edge_info = cls.create_default_data()
        json_utils.export_bundle(
            json_utils.get_default_file_path('task_graph'),
            src_map=src_map,
            dst_map=dst_map,
            task_info=task_info,
            edge_info=edge_info,
        )
        src_map, dst_map, task_info, edge_info = json_utils.import_bundle(
            json_utils.get_default_file_path('task_graph'),
            'src_map', 'dst_map', 'task_info', 'edge_info',
        )
        return cls.create(src_map, dst_map, task_info, edge_info)

    @classmethod
    def create_default_data(cls):
        log.info('create default task graph')
        src_map = {
            'src_thermal.0': 'THERMAL.0',
            'src_thermal.1': 'THERMAL.1',
            'src_camera': 'CAMERA.0',
        }
        dst_map = {
            'dst_broadcast': 'BROADCAST.0',
        }
        task_info = {
            'task_getAvgTemperature': {
                GtInfo.LATENCY_INFO: {
                    Device.T2_MICRO: {
                        # TODO: assume one flavor per device type for now.
                        # may extend to multiple flavor later
                        Flavor.CPU: Unit.ms(15),
                    },
                    Device.T3_LARGE: {
                        Flavor.CPU: Unit.ms(10),
                    },
                    Device.P3_2XLARGE: {
                        Flavor.CPU: Unit.ms(5),
                    },
                },
                GtInfo.RESRC_RQMT: {
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
                    Device.T2_MICRO: {
                        Flavor.CPU: Unit.sec(6),
                    },
                    Device.T3_LARGE: {
                        Flavor.CPU: Unit.sec(2),
                    },
                    Device.P3_2XLARGE: {
                        Flavor.GPU: Unit.ms(600),
                    },
                },
                GtInfo.RESRC_RQMT: {
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
                    Device.T2_MICRO: {
                        Flavor.CPU: Unit.ms(5),
                    },
                    Device.T3_LARGE: {
                        Flavor.CPU: Unit.ms(5),
                    },
                    Device.P3_2XLARGE: {
                        Flavor.CPU: Unit.ms(5),
                    },
                },
                GtInfo.RESRC_RQMT: {
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
                    Device.T2_MICRO: {
                        Flavor.CPU: Unit.ms(5),
                    },
                    Device.T3_LARGE: {
                        Flavor.CPU: Unit.ms(5),
                    },
                    Device.P3_2XLARGE: {
                        Flavor.CPU: Unit.ms(5),
                    },
                },
                GtInfo.RESRC_RQMT: {
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
            'src_thermal.0 -> task_getAvgTemperature': {
                GtInfo.TRAFFIC: Unit.kbyte(1),
            },
            'src_thermal.1 -> task_getAvgTemperature': {
                GtInfo.TRAFFIC: Unit.kbyte(1),
            },
            'src_camera -> task_findObject': {
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
            'task_sentNotificatoin -> dst_broadcast': {
                GtInfo.TRAFFIC: Unit.byte(1),
            },
        }
        return src_map, dst_map, task_info, edge_info

    @staticmethod
    def plot(graph):
        nx.draw_networkx(
            graph,
            pos=nx.spring_layout(graph),
            arrows=False,
            with_labels=True,
        )
        plt.show(graph)
