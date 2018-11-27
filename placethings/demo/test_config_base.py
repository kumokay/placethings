from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config.base import nw_device_cfg
from placethings.demo.base_test import BaseTestCase

log = logging.getLogger()

"""
network settings

  home_sw1   home_sw2  home_sw3
      |         |         |
    bb_sw1 -- bb_sw2 -- bb_sw3
      |         |         |
    bb_ap1    bb_ap2    bb_ap3
"""


class TestDefineConfig(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None

        nw_device_spec = nw_device_cfg.NetworkDeviceSpec()

        nw_device = nw_device_cfg.NetworkDevice('juniper_ex4300')
        nw_device.add_interface('WAN', nw_device_cfg.NetworkInterface(
            protocol='ethernet', n_ports=24, ul_bw='1Gb',
            dl_bw='1Gb'))
        nw_device_spec.add_nw_device(nw_device)

        nw_device = nw_device_cfg.NetworkDevice('dlink_ac3900')
        nw_device.add_interface('LAN', nw_device_cfg.NetworkInterface(
            protocol='wifi', n_ports=10, ul_bw='100Mb',
            dl_bw='100Mb'))
        nw_device.add_interface('WAN', nw_device_cfg.NetworkInterface(
            protocol='ethernet', n_ports=1, ul_bw='1000Mb',
            dl_bw='1000Mb'))
        nw_device_spec.add_nw_device(nw_device)

        nw_device = nw_device_cfg.NetworkDevice('dlink_dgs105')
        nw_device.add_interface('LAN', nw_device_cfg.NetworkInterface(
            protocol='ethernet', n_ports=4, ul_bw='100Mb',
            dl_bw='100Mb'))
        nw_device.add_interface('WAN', nw_device_cfg.NetworkInterface(
            protocol='ethernet', n_ports=1, ul_bw='1000Mb',
            dl_bw='1000Mb'))
        nw_device_spec.add_nw_device(nw_device)

        nw_device_inventory = nw_device_cfg.NetworkDeviceInventory(
            nw_device_spec)
        nw_device_inventory.add_device('bb_sw1', 'juniper_ex4300')
        nw_device_inventory.add_device('bb_sw2', 'juniper_ex4300')
        nw_device_inventory.add_device('bb_sw3', 'juniper_ex4300')
        nw_device_inventory.add_device('bb_ap1', 'dlink_ac3900')
        nw_device_inventory.add_device('bb_ap2', 'dlink_ac3900')
        nw_device_inventory.add_device('bb_ap3', 'dlink_ac3900')
        nw_device_inventory.add_device('home_sw1', 'dlink_dgs105')
        nw_device_inventory.add_device('home_sw2', 'dlink_dgs105')
        nw_device_inventory.add_device('home_sw3', 'dlink_dgs105')

        nw_device_data = nw_device_cfg.NetworkDeviceData(nw_device_inventory)
        network_link = nw_device_cfg.NetworkLink('WAN', 'WAN', 2)
        # bb_sw1 <-> bb_sw2
        nw_device_data.add_link('bb_sw1', 'bb_sw2', network_link)
        nw_device_data.add_link('bb_sw2', 'bb_sw1', network_link)
        # bb_sw2 <-> bb_sw3
        nw_device_data.add_link('bb_sw2', 'bb_sw3', network_link)
        nw_device_data.add_link('bb_sw3', 'bb_sw2', network_link)
        # bb_sw1 <-> bb_ap1
        nw_device_data.add_link('bb_sw1', 'bb_ap1', network_link)
        nw_device_data.add_link('bb_ap1', 'bb_sw1', network_link)
        # bb_sw2 <-> bb_ap2
        nw_device_data.add_link('bb_sw2', 'bb_ap2', network_link)
        nw_device_data.add_link('bb_ap2', 'bb_sw2', network_link)
        # bb_sw3 <-> bb_ap3
        nw_device_data.add_link('bb_sw3', 'bb_ap3', network_link)
        nw_device_data.add_link('bb_ap3', 'bb_sw3', network_link)
        # home_sw1 <-> bb_sw1
        nw_device_data.add_link('bb_sw1', 'home_sw1', network_link)
        nw_device_data.add_link('home_sw1', 'bb_sw1', network_link)
        # home_sw2 <-> bb_sw2
        nw_device_data.add_link('bb_sw2', 'home_sw2', network_link)
        nw_device_data.add_link('home_sw2', 'bb_sw2', network_link)
        # home_sw3 <-> bb_sw3
        nw_device_data.add_link('bb_sw3', 'home_sw3', network_link)
        nw_device_data.add_link('home_sw3', 'bb_sw3', network_link)

        nw_device_data.export_to_file('config_base/nw_device_data.json')
