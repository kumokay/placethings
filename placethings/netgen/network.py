from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from placethings.netgen.netmanager import NetManager
from placethings.definition import (
    GInfo, GnInfo, GdInfo, NwLink, NodeType, Device)


log = logging.getLogger()


_PKT_LOSS = {
    NwLink.WIFI: 0.0,
    NwLink.ETHERNET: 0.0,
}


class ControlPlane(object):

    _cmd_agent_template = (
        'cd {progdir} && python main_entity.py run_agent '
        '-n {name} -a {ip}:{port}')
    _manager_name = 'Manager'

    def __init__(self, Gn):
        self.net = NetManager.create()
        for node in Gn.nodes():
            node_type = Gn.node[node][GInfo.NODE_TYPE]
            if node_type == NodeType.DEVICE:
                self.net.addHost(node)
            elif node_type == NodeType.NW_DEVICE:
                self.net.addSwitch(node)
            else:
                assert False, 'unkown node_type: {}'.format(node_type)
        for d1, d2 in Gn.edges():
            edge_info = Gn[d1][d2]
            self.net.addLink(
                d1, d2,
                bw_bps=edge_info[GnInfo.BANDWIDTH],
                delay_ms=edge_info[GnInfo.LATENCY],
                pkt_loss_rate=_PKT_LOSS[edge_info[GnInfo.PROTOCOL]])

    def runAgent(self, device_name, agent_name, progdir, ip, port):
        command = self._cmd_agent_template.format(
            progdir=progdir,
            name=agent_name,
            ip=ip,
            port=port)
        self.net.run_cmd(device_name, command, async=True)

    def addManager(self, device_name):
        self.net.addHost(self._manager_name)
        self.net.addLink(
            self._manager_name, device_name,
            bw_bps=None,
            delay_ms=0,
            pkt_loss_rate=0)

    def runManageCmd(self, command):
        self.net.run_cmd(self._manager_name, command, async=False)


class DataPlane(object):

    _cmd_actuator_template = (
        'cd {progdir} && python main_entity.py run_actuator '
        '-n {name} -a {ip}:{port}')
    _cmd_sensor_template = (
        'cd {progdir} && python main_entity.py run_sensor '
        '-n {name} -a {ip}:{port} -st {sensor_type} -ra {next_ip}:{next_port}')
    _cmd_task_template = (
        'cd {progdir} && python main_entity.py run_task '
        '-a {ip}:{port} -n {name} -t {exectime} -ra {next_ip}:{next_port}')

    def __init__(self, Gn):
        self.worker_dict = {}  # worker_name: (device_name, worker_start_cmd)
        self.device_dict = {}
        self.net = NetManager.create()
        for node in Gn.nodes():
            node_type = self.Gn.node[node][GInfo.NODE_TYPE]
            if node_type == NodeType.DEVICE:
                self.device_dict[node] = self.Gn.node[node][GdInfo.DEVICE_TYPE]
            self.net.addSwitch(node)
        for d1, d2 in Gn.edges():
            edge_info = Gn[d1][d2]
            self.net.addLink(
                d1, d2,
                bw_bps=edge_info[GnInfo.BANDWIDTH],
                delay_ms=edge_info[GnInfo.LATENCY],
                pkt_loss_rate=_PKT_LOSS[edge_info[GnInfo.PROTOCOL]])

    def _check_device(self, device_name, expect_device_type):
        dev_type = self.device_dict[device_name]
        assert dev_type == expect_device_type

    def _addWorker(self, name, device_name, run_worker_cmd):
        self.net.addHost(name)
        self.net.addLink(
            name, device_name,
            bw_bps=None,
            delay_ms=0,
            pkt_loss_rate=0)
        self.worker_dict[name] = (device_name, run_worker_cmd)

    def _runWorker(self, name):
        assert name in self.worker_dict
        _, run_worker_cmd = self.worker_dict[name]
        self.net.run_cmd(name, run_worker_cmd, async=True)

    def _stopWorker(self, name):
        assert False, 'not implemented'
        pass

    def _moveWorker(self, name, from_device, to_device):
        assert name in self.worker_dict
        self.net.delLink(name, from_device)
        self.net.addLink(
            name, to_device,
            bw_bps=None,
            delay_ms=0,
            pkt_loss_rate=0)

    def addActuator(self, device_name, worker_name, progdir, ip, port):
        self._check_device(device_name, Device.ACTUATOR)
        cmd = self._cmd_actuator_template.format(
            progdir=progdir,
            name=worker_name,
            ip=ip,
            port=port)
        self._addWorker(worker_name, device_name, cmd)

    def runSensor(
            self, device_name, worker_name,
            progdir, ip, port, sensor_type, next_ip, next_port):
        self._check_device(device_name, Device.SENSOR)
        cmd = self._cmd_sensor_template.format(
            progdir=progdir,
            name=worker_name,
            ip=ip,
            port=port,
            sensor_type=sensor_type,
            next_ip=next_ip,
            next_port=next_port)
        self._addWorker(worker_name, device_name, cmd)

    def runTask(
            self, device_name, worker_name,
            progdir, ip, port, exectime, next_ip, next_port):
        self._check_device(device_name, Device.PROCESSOR)
        cmd = self._cmd_task_template.format(
            progdir=progdir,
            name=worker_name,
            ip=ip,
            port=port,
            exectime=exectime,
            next_ip=next_ip,
            next_port=next_port)
        self._addWorker(worker_name, device_name, cmd)


class NetGen(object):

    _PKT_LOSS = {
        NwLink.WIFI: 0.0,
        NwLink.ETHERNET: 0.0,
    }

    @classmethod
    def create_control_plane(cls, Gn):
        """
        Create an empty network and add nodes to it.

        Args:
            Gn (nx.DiGraph): topo_device_graph
        Returns:
            net (NetManager): a network of switches and devices
        """
        return cls.create(Gn)

    def create_data_plane(cls, Gn):
        """
        Args:
            Gn (nx.DiGraph): topo_device_graph
        Returns:
            net (NetManager): a network of all switches
        """
        net = NetManager.create()
        for node in Gn.nodes():
            node_type = Gn.node[node][GInfo.NODE_TYPE]
            if node_type == NodeType.DEVICE:
                net.addSwitch(node)
            elif node_type == NodeType.NW_DEVICE:
                net.addSwitch(node)
            else:
                assert False, 'unkown node_type: {}'.format(node_type)
        for d1, d2 in Gn.edges():
            edge_info = Gn[d1][d2]
            net.addLink(
                d1, d2,
                bw_bps=edge_info[GnInfo.BANDWIDTH],
                delay_ms=edge_info[GnInfo.LATENCY],
                pkt_loss_rate=cls._PKT_LOSS[edge_info[GnInfo.PROTOCOL]])
        return net

    @classmethod
    def create(cls, Gn):
        """
        Create an empty network and add nodes to it.

        Args:
            Gn (nx.DiGraph): topo_device_graph
        Returns:
            net (NetManager)
        """
        net = NetManager.create()
        for node in Gn.nodes():
            node_type = Gn.node[node][GInfo.NODE_TYPE]
            if node_type == NodeType.DEVICE:
                net.addHost(node)
            elif node_type == NodeType.NW_DEVICE:
                net.addSwitch(node)
            else:
                assert False, 'unkown node_type: {}'.format(node_type)
        for d1, d2 in Gn.edges():
            edge_info = Gn[d1][d2]
            net.addLink(
                d1, d2,
                bw_bps=edge_info[GnInfo.BANDWIDTH],
                delay_ms=edge_info[GnInfo.LATENCY],
                pkt_loss_rate=cls._PKT_LOSS[edge_info[GnInfo.PROTOCOL]])
        return net
