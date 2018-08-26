from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from future.utils import iteritems

import networkx as nx

from placethings.definition import Const, Device, GdInfo, GnInfo, Hardware
from placethings.topology import TopoGraph
from placethings.utils import Unit


log = logging.getLogger()


class NetworkGraph(object):

    _DEFAULT_DEVICE_TO_SWITCH_RATIO = 5

    @staticmethod
    def _add_nodes(graph, device_info):
        for name, attr in iteritems(device_info):
            graph.add_node(name, **attr)

    @staticmethod
    def _add_edges(graph, topo_graph):
        for src in graph.nodes():
            for dst in graph.nodes():
                if src == dst:
                    continue
                try:
                    total_latency = nx.shortest_path_length(
                        topo_graph,
                        source=src,
                        target=dst,
                        weight=GnInfo.LATENCY)
                except nx.NetworkXNoPath:
                    total_latency = Const.INT_MAX
                attr = {
                    GdInfo.LATENCY: total_latency,
                }
                graph.add_edge(src, dst, **attr)

    @classmethod
    def create(cls, device_info, topo_graph):
        """
        Args:
            device_info (dict): device attributes
            topo_graph (networkx.DiGraph): how computing devices connected to
                network devices (routers, switches, APs)
        Returns:
            network_graph (networkx.DiGraph): end-to-end relationship between
                computing devices
        """
        graph = nx.DiGraph()
        # create graph from input data
        cls._add_nodes(graph, device_info)
        cls._add_edges(graph, topo_graph)
        return graph

    @classmethod
    def create_default_graph(cls):
        # generate default device info
        device_type_spec, device_inventory = cls.create_default_data()
        all_device_info = cls.derive_device_info(
            device_type_spec, device_inventory)

        # generate default topology
        device_list = list(all_device_info)
        n_switch = len(device_list) // cls._DEFAULT_DEVICE_TO_SWITCH_RATIO
        switch_list = TopoGraph.create_default_switch_list(n_switch)
        topo_graph = TopoGraph.create_default_topo(device_list, switch_list)

        # generate network graph
        graph = cls.create(all_device_info, topo_graph)
        return graph

    @staticmethod
    def _gen_device_name(device_type, device_id):
        return '{}.{}'.format(device_type.name, device_id)

    @classmethod
    def derive_device_info(cls, device_type_spec, device_inventory):
        all_device_info = {}
        for device_type, n_device in iteritems(device_inventory):
            for device_id in range(n_device):
                device_name = cls._gen_device_name(device_type, device_id)
                # copy hardware spec
                device_info = {}
                device_info[GdInfo.HARDWARE_SPEC] = (
                    device_type_spec[device_type][GdInfo.HARDWARE_SPEC])
                # derive resource info
                device_info[GdInfo.RESOURCE] = {}
                for key, value in iteritems(device_info[GdInfo.HARDWARE_SPEC]):
                    # set cpu, gpu to be 100
                    if key in [Hardware.CPU, Hardware.GPU]:
                        device_info[GdInfo.RESOURCE][key] = (
                            Unit.percentage(100))
                    else:
                        device_info[GdInfo.RESOURCE][key] = value
                all_device_info[device_name] = device_info
        return all_device_info

    @staticmethod
    def create_default_data():
        log.info('create default device data')
        device_type_spec = {
            Device.T2_MICRO: {
                GdInfo.COST: Unit.rph(0.0116),
                GdInfo.HARDWARE_SPEC: {
                    Hardware.RAM: Unit.gbyte(1),
                    Hardware.HD: Unit.gbyte(30),
                    Hardware.CPU: 1,
                    Hardware.GPU: 0,
                    Hardware.NIC_INGRESS: Unit.mbps(100),
                    Hardware.NIC_EGRESS: Unit.mbps(100),
                },
            },
            Device.T3_LARGE: {
                GdInfo.COST: Unit.rph(0.0928),
                GdInfo.HARDWARE_SPEC: {
                    Hardware.RAM: Unit.gbyte(8),
                    Hardware.HD: Unit.tbyte(16),
                    Hardware.CPU: 2,
                    Hardware.GPU: 0,
                    Hardware.NIC_INGRESS: Unit.gbps(1),
                    Hardware.NIC_EGRESS: Unit.gbps(1),
                },
            },
            Device.P3_2XLARGE: {
                GdInfo.COST: Unit.rph(3.06),
                GdInfo.HARDWARE_SPEC: {
                    Hardware.RAM: Unit.gbyte(16),
                    Hardware.HD: Unit.tbyte(16),
                    Hardware.CPU: 8,
                    Hardware.GPU: 1,
                    Hardware.NIC_INGRESS: Unit.gbps(10),
                    Hardware.NIC_EGRESS: Unit.gbps(10),
                },
            },
        }
        device_inventory = {
            Device.T2_MICRO: 20,
            Device.T3_LARGE: 10,
            Device.P3_2XLARGE: 1,
        }
        return device_type_spec, device_inventory
