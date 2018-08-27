from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import range
from copy import deepcopy
import logging
from future.utils import iteritems

import networkx as nx

from placethings.definition import (
    Const, Device, DeviceCategory, GdInfo, GnInfo, Hardware)
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
    def create_default_device_info(cls):
        # generate default device info
        device_spec, device_inventory = cls.create_default_data()
        return cls.derive_device_info(device_spec, device_inventory)

    @classmethod
    def create_default_graph(cls):
        all_device_info = cls.create_default_device_info()
        n_switch = len(all_device_info) // cls._DEFAULT_DEVICE_TO_SWITCH_RATIO
        switch_list = TopoGraph.create_default_switch_list(n_switch)
        topo_graph = TopoGraph.create_default_topo(
            switch_list, list(all_device_info))

        # generate network graph
        graph = cls.create(all_device_info, topo_graph)
        return graph

    @staticmethod
    def _gen_device_name(device_type, device_id):
        return '{}.{}'.format(device_type.name, device_id)

    @classmethod
    def derive_device_info(cls, device_spec, device_inventory):
        all_device_info = {}
        for device_cat, device_inventory_info in iteritems(device_inventory):
            for device_type, n_device in iteritems(device_inventory_info):
                for device_id in range(n_device):
                    device_name = cls._gen_device_name(device_type, device_id)
                    # copy hardware spec
                    spec = device_spec[device_cat][device_type]
                    device_info = {
                        GdInfo.DEVICE_CAT: device_cat,
                        GdInfo.DEVICE_TYPE: device_type,
                        GdInfo.COST: spec[GdInfo.COST],
                        GdInfo.HARDWARE: spec[GdInfo.HARDWARE],
                        GdInfo.RESRC: deepcopy(spec[GdInfo.HARDWARE]),
                    }
                    # special setting for RESRC info of GPU/CPU
                    for hw_type in [Hardware.CPU, Hardware.GPU]:
                        if hw_type in device_info[GdInfo.RESRC]:
                            device_info[GdInfo.RESRC][hw_type] = (
                                Unit.percentage(100))
                    all_device_info[device_name] = device_info
        return all_device_info

    @staticmethod
    def create_default_data():
        log.info('create default device data')
        device_inventory = {
            DeviceCategory.ACTUATOR: {
                Device.BROADCAST: 1,
            },
            DeviceCategory.PROCESSOR: {
                Device.T2_MICRO: 20,
                Device.T3_LARGE: 10,
                Device.P3_2XLARGE: 1,
            },
            DeviceCategory.SENSOR: {
                Device.THERMAL: 2,
                Device.CAMERA: 1,
            },
        }
        device_spec = {
            DeviceCategory.ACTUATOR: {
                Device.BROADCAST: {
                    GdInfo.COST: Unit.rph(0),
                    GdInfo.HARDWARE: {},
                },
            },
            DeviceCategory.PROCESSOR: {
                Device.T2_MICRO: {
                    GdInfo.COST: Unit.rph(0.0116),
                    GdInfo.HARDWARE: {
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
                    GdInfo.HARDWARE: {
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
                    GdInfo.HARDWARE: {
                        Hardware.RAM: Unit.gbyte(16),
                        Hardware.HD: Unit.tbyte(16),
                        Hardware.CPU: 8,
                        Hardware.GPU: 1,
                        Hardware.NIC_INGRESS: Unit.gbps(10),
                        Hardware.NIC_EGRESS: Unit.gbps(10),
                    },
                },
            },
            DeviceCategory.SENSOR: {
                Device.THERMAL: {
                    GdInfo.COST: Unit.rph(0),
                    GdInfo.HARDWARE: {},
                },
                Device.CAMERA: {
                    GdInfo.COST: Unit.rph(0),
                    GdInfo.HARDWARE: {},
                },
            },
        }
        return device_spec, device_inventory
