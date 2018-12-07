from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config.base import device_cfg
from placethings.demo.base_test import BaseTestCase
from placethings.utils import plot_utils

log = logging.getLogger()

"""
network settings

  home_sw1   home_sw2  home_sw3
      |         |         |
    bb_sw1 -- bb_sw2 -- bb_sw3
      |         |         |
    bb_ap1    bb_ap2    bb_ap3
"""


def create_network_device_spec():
    device_spec = device_cfg.DeviceSpec()

    device = device_cfg.NetworkDevice(network=device_cfg.Network())
    device.network.add_interface('ingress', device_cfg.NetworkInterface(
        protocol='ethernet', n_ports=24, ul_bw='1Gb', dl_bw='1Gb'))
    device.network.add_interface('egress', device_cfg.NetworkInterface(
        protocol='ethernet', n_ports=24, ul_bw='1Gb', dl_bw='1Gb'))
    device_spec.add_device('juniper_ex4300', device)

    device = device_cfg.NetworkDevice(network=device_cfg.Network())
    device.network.add_interface('ingress', device_cfg.NetworkInterface(
        protocol='wifi', n_ports=10, ul_bw='100Mb', dl_bw='100Mb'))
    device.network.add_interface('egress', device_cfg.NetworkInterface(
        protocol='ethernet', n_ports=1, ul_bw='1Gb', dl_bw='1Gb'))
    device_spec.add_device('dlink_ac3900', device)

    device = device_cfg.NetworkDevice(network=device_cfg.Network())
    device.network.add_interface('ingress', device_cfg.NetworkInterface(
        protocol='ethernet', n_ports=10, ul_bw='100Mb', dl_bw='100Mb'))
    device.network.add_interface('egress', device_cfg.NetworkInterface(
        protocol='ethernet', n_ports=1, ul_bw='1Gb', dl_bw='1Gb'))
    device_spec.add_device('dlink_dgs105', device)

    return device_spec


def create_default_spec():
    device_spec = create_network_device_spec()

    network = device_cfg.Network(
        interface_dict=dict(egress=device_cfg.NetworkInterface(
            protocol='ethernet', n_ports=1, ul_bw='10Gb', dl_bw='10Gb')))
    comp_resource = device_cfg.ComputationResource(
        cpu_utilization='100%', gpu_utilization='100%', disk_space='100GB',
        ram_size='64GB')
    device = device_cfg.Device(
        network=network,
        processor=device_cfg.Processor(computation_resource=comp_resource))
    device_spec.add_device('p3.2xlarge', device)

    network = device_cfg.Network(
        interface_dict=dict(egress=device_cfg.NetworkInterface(
            protocol='ethernet', n_ports=1, ul_bw='400Mb', dl_bw='400Mb')))
    comp_resource = device_cfg.ComputationResource(
        cpu_utilization='100%', gpu_utilization='0%', disk_space='100GB',
        ram_size='8GB')
    device = device_cfg.Device(
        network=network,
        processor=device_cfg.Processor(computation_resource=comp_resource))
    device_spec.add_device('t3.large', device)

    network = device_cfg.Network(
        interface_dict=dict(egress=device_cfg.NetworkInterface(
            protocol='ethernet', n_ports=1, ul_bw='100Mb', dl_bw='100Mb')))
    comp_resource = device_cfg.ComputationResource(
        cpu_utilization='100%', gpu_utilization='0%', disk_space='20GB',
        ram_size='1GB')
    device = device_cfg.Device(
        network=network,
        processor=device_cfg.Processor(computation_resource=comp_resource))
    device_spec.add_device('t3.micro', device)

    network = device_cfg.Network(
        interface_dict=dict(egress=device_cfg.NetworkInterface(
            protocol='wifi', n_ports=1, ul_bw='600Mb', dl_bw='600Mb')))
    device = device_cfg.Device(network=network)
    device.add_actuator('notification_app', device_cfg.Actuator(
        auctuator_type='msg_display'))
    device_spec.add_device('phone', device)

    network = device_cfg.Network(
        interface_dict=dict(egress=device_cfg.NetworkInterface(
            protocol='wifi', n_ports=1, ul_bw='600Mb', dl_bw='600Mb')))
    device = device_cfg.Device(network=network)
    device.add_sensor('drone_camera', device_cfg.Sensor(sensor_type='camera'))
    device_spec.add_device('drone', device)

    return device_spec


class TestDefineNwConfig(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None

        device_spec = create_network_device_spec()
        device_data = device_cfg.DeviceData(device_spec=device_spec)
        device_data.add_device('bb_sw1', 'juniper_ex4300')
        device_data.add_device('bb_sw2', 'juniper_ex4300')
        device_data.add_device('bb_sw3', 'juniper_ex4300')
        device_data.add_device('home_ap1', 'dlink_ac3900')
        device_data.add_device('home_ap2', 'dlink_ac3900')
        device_data.add_device('home_ap3', 'dlink_ac3900')
        device_data.add_device('home_sw1', 'dlink_dgs105')
        device_data.add_device('home_sw2', 'dlink_dgs105')
        device_data.add_device('home_sw3', 'dlink_dgs105')

        network_link = device_cfg.NetworkLink('egress', 'ingress', '2ms')
        device_data.add_link('bb_sw1', 'bb_sw2', network_link)
        device_data.add_link('bb_sw2', 'bb_sw3', network_link)
        device_data.add_link('home_ap1', 'bb_sw1', network_link)
        device_data.add_link('home_ap2', 'bb_sw2', network_link)
        device_data.add_link('home_ap3', 'bb_sw3', network_link)
        device_data.add_link('home_sw1', 'bb_sw1', network_link)
        device_data.add_link('home_sw2', 'bb_sw2', network_link)
        device_data.add_link('home_sw3', 'bb_sw3', network_link)

        graph = device_data.to_graph()
        plot_utils.plot(graph, filepath='config_base/nw_device_data.png')

        device_data.export_to_file('config_base/nw_device_data.json')
        device_data_imported = device_cfg.DeviceData().import_from_file(
            'config_base/nw_device_data.json')
        assert device_data_imported.to_json() == device_data.to_json()


class TestDefineConfig(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None

        device_spec = create_default_spec()
        device_data = device_cfg.DeviceData(device_spec=device_spec)

        device_data.add_device('bb_sw1', 'juniper_ex4300')
        device_data.add_device('bb_sw2', 'juniper_ex4300')
        device_data.add_device('bb_sw3', 'juniper_ex4300')
        device_data.add_device('home_ap1', 'dlink_ac3900')
        device_data.add_device('home_ap2', 'dlink_ac3900')
        device_data.add_device('home_ap3', 'dlink_ac3900')
        device_data.add_device('home_sw1', 'dlink_dgs105')
        device_data.add_device('home_sw2', 'dlink_dgs105')
        device_data.add_device('home_sw3', 'dlink_dgs105')

        device_data.add_device('nuc', 't3.micro')
        device_data.add_device('cpu_server', 't3.large')
        device_data.add_device('gpu_server', 'p3.2xlarge')
        device_data.add_device('samsung_phone', 'phone')
        device_data.add_device('patroller_drone', 'drone')

        network_link = device_cfg.NetworkLink('egress', 'ingress', '2ms')
        device_data.add_link('bb_sw1', 'bb_sw2', network_link)
        device_data.add_link('bb_sw2', 'bb_sw3', network_link)
        device_data.add_link('home_ap1', 'bb_sw1', network_link)
        device_data.add_link('home_ap2', 'bb_sw2', network_link)
        device_data.add_link('home_ap3', 'bb_sw3', network_link)
        device_data.add_link('home_sw1', 'bb_sw1', network_link)
        device_data.add_link('home_sw2', 'bb_sw2', network_link)
        device_data.add_link('home_sw3', 'bb_sw3', network_link)

        device_data.add_link('gpu_server', 'home_sw1', network_link)
        device_data.add_link('cpu_server', 'home_sw2', network_link)
        device_data.add_link('nuc', 'home_sw3', network_link)
        device_data.add_link('samsung_phone', 'home_ap1', network_link)
        device_data.add_link('patroller_drone', 'home_ap2', network_link)

        graph = device_data.to_graph()
        plot_utils.plot(graph, filepath='config_base/all_device_data.png')

        device_data.export_to_file('config_base/all_device_data.json')
        device_data_imported = device_cfg.DeviceData().import_from_file(
            'config_base/all_device_data.json')
        assert device_data_imported.to_json() == device_data.to_json()
