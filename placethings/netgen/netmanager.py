from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from mininet.clean import cleanup
from mininet.net import Containernet
from mininet.link import TCLink
from mininet.node import Controller, OVSSwitch
from mininet.log import setLogLevel as mininet_SetLogLevel


mininet_SetLogLevel('info')
log = logging.getLogger()


class NetManager(object):
    _NEXT_IP_NUM = 100
    _NEXT_DOCKER_IP_NUM = 2
    _NEXT_HOST_ID = 0
    _NEXT_SWITCH_ID = 0
    _HOST_PREFIX = 'h'
    _SWITCH_PREFIX = 's'
    _PORT_START = 18800

    def __init__(self, net):
        self._net = net
        self._host_dict = {}
        self._host_ip_dict = {}  # assigned host ip
        self._host_docker_ip_dict = {}
        self._host_next_free_port = {}
        self._switch_dict = {}
        self._edge_dict = {}
        self._devNameToNodeName = {}
        self._device_ips = {}

    def get_host_list(self):
        return list(self._host_dict)

    @classmethod
    def create(cls):
        raw_net = Containernet(controller=Controller, link=TCLink)
        log.info('create mininet wtih default controller')
        raw_net.addController('c0')
        return cls(raw_net)

    @classmethod
    def _new_ip(cls):
        ip = '10.0.0.{}'.format(cls._NEXT_IP_NUM)
        docker_ip = '172.18.0.{}'.format(cls._NEXT_DOCKER_IP_NUM)
        cls._NEXT_IP_NUM += 1
        cls._NEXT_DOCKER_IP_NUM += 1
        assert cls._NEXT_IP_NUM < 256
        assert cls._NEXT_DOCKER_IP_NUM < 256
        return ip, docker_ip

    @classmethod
    def _new_host_name(cls):
        name = '{}{}'.format(cls._HOST_PREFIX, cls._NEXT_HOST_ID)
        cls._NEXT_HOST_ID += 1
        return name

    @classmethod
    def _new_switch_name(cls):
        name = '{}{}'.format(cls._SWITCH_PREFIX, cls._NEXT_SWITCH_ID)
        cls._NEXT_SWITCH_ID += 1
        return name

    def addHost(self, device_name):
        # auto generate name bc name cannot be too long =.=
        name = self._new_host_name()
        # TODO: use cmd to get correct docker ip
        ip, docker_ip = self._new_ip()
        host = self._net.addDocker(
            name, ip=ip, dimage="kumokay/ubuntu_wifi:v6")
        self._host_dict[device_name] = host
        self._host_ip_dict[device_name] = ip
        self._host_docker_ip_dict[device_name] = docker_ip
        self._host_next_free_port[device_name] = self._PORT_START
        self._devNameToNodeName[device_name] = name
        log.debug('add host {}'.format(device_name))

    def addSwitch(self, device_name):
        name = self._new_switch_name()
        switch = self._net.addSwitch(name, cls=OVSSwitch)
        self._switch_dict[device_name] = switch
        self._devNameToNodeName[device_name] = name
        log.debug('add switch {}'.format(device_name))

    def addLink(
            self, src, dst, bw_bps=None, delay_ms=1,
            max_queue_size=None, pkt_loss_rate=None):
        if (dst, src) in self._edge_dict:
            # mininet is not DiGraph! everything is bidirectional
            return
        # mininet bandwidth supported range 0..1000
        if bw_bps is None:
            bw_mbps = None
        else:
            bw_mbps = None if bw_bps > 1000000 else int(bw_bps / 1000000)
        delay = '{}ms'.format(delay_ms)
        loss = int(pkt_loss_rate*100) if pkt_loss_rate else None
        link = self._net.addLink(
            self._devNameToNodeName[src], self._devNameToNodeName[dst],
            bw=bw_mbps, delay=delay, max_queue_size=max_queue_size, loss=loss)
        self._edge_dict[(src, dst)] = link
        log.debug('link {} <-> {}: delay={}'.format(src, dst, delay))

    def delLink(self, src, dst):
        if (src, dst) in self._edge_dict:
            assert (dst, src) not in self._edge_dict
            self._net.removeLink(
                node1=self._devNameToNodeName[src],
                node2=self._devNameToNodeName[dst])
            del self._edge_dict[(src, dst)]
        elif (dst, src) in self._edge_dict:
            self._net.removeLink(
                node1=self._devNameToNodeName[dst],
                node2=self._devNameToNodeName[src])
            del self._edge_dict[(dst, src)]
        log.debug('delete link {} <-> {}'.format(src, dst))

    def modifyLinkDelay(self, src, dst, delay_ms):
        delay = '{}ms'.format(delay_ms)
        edge = (src, dst)
        if edge not in self._edge_dict:
            edge = (dst, src)
        link = self._edge_dict[edge]
        link.intf1.config(delay=delay)
        log.debug('modify link {} <-> {}'.format(src, dst))

    def modifyLink(
            self, src, dst, new_dst=None, bw_bps=None, delay_ms=1,
            max_queue_size=None, pkt_loss_rate=None):
        if not new_dst:
            new_dst = dst
        self.delLink(src, dst)
        self.addLink(
            src, new_dst,
            bw_bps, delay_ms, max_queue_size, pkt_loss_rate)

    def start(self):
        log.info('*** Starting network')
        self._net.start()

    def stop(self):
        log.info('*** Stopping network')
        self._net.stop()
        # TODO: this is a hotfix. should stop hosts properly
        cleanup()

    def run_cmd(self, device_name, command, async=False):
        host = self._host_dict[device_name]
        log.info('send command: {}'.format(command))
        if async:
            # no waiting
            host.sendCmd(command)
            output = 'command sent'
        else:
            output = host.cmd(command)
        log.info('output: {}'.format(output))
        return output

    def get_device_ip(self, device_name):
        ip = self._host_ip_dict[device_name]
        # ip = self._host_dict[device_name].IP()
        assert ip is not None, 'host={}, ip={}'.format(device_name, ip)
        return ip

    def get_device_docker_ip(self, device_name):
        ip = self._host_docker_ip_dict[device_name]
        # ip = self._host_dict[device_name].IP()
        assert ip is not None, 'host={}, docker_ip={}'.format(device_name, ip)
        return ip

    def get_device_free_port(self, device_name):
        next_port = self._host_next_free_port[device_name]
        self._host_next_free_port[device_name] += 1
        return next_port

    def validate(self):
        log.info('*** Validate network')
        for h1 in self._host_dict:
            for h2 in self._host_dict:
                if h1 == h2:
                    continue
                output = self.run_cmd(
                    h1, 'ping {} -c 1'.format(self._host_dict[h2].IP()))
                assert ' 0% packet loss' in output, output
        log.info('ping all success!')
