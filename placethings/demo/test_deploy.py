from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time

from placethings.netgen.network import ControlPlane, DataPlane
from placethings.demo.utils import ConfigDataHelper
from placethings.demo.base_test import BaseTestCase
from placethings.definition import GnInfo, Unit

log = logging.getLogger()


def _init_netsim(topo_device_graph, Gd, G_map):
    # simulate network
    control_plane = ControlPlane(topo_device_graph)
    control_plane.add_manager('HOME_ROUTER.0')
    control_plane.deploy_agent()
    # control_plane.runAgent()
    data_plane = DataPlane(topo_device_graph)
    data_plane.add_manager('HOME_ROUTER.0')
    data_plane.deploy_task(G_map, Gd)
    return control_plane, data_plane


class TestBasic(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=True):
        cfgHelper = ConfigDataHelper(config_name, is_export)
        cfgHelper.init_task_graph()
        cfgHelper.update_topo_device_graph()
        cfgHelper.update_task_map()
        _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        # simulate
        control_plane, data_plane = _init_netsim(topo_device_graph, Gd, G_map)
        # cleanup
        data_plane.start(is_validate=True)
        data_plane.stop()


class TestDynamic(BaseTestCase):
    @staticmethod
    def _simulate(topo_device_graph, Gd, G_map):
        control_plane, data_plane = _init_netsim(topo_device_graph, Gd, G_map)
        data_plane.start(is_validate=True)
        time.sleep(30)
        data_plane.stop()

    @classmethod
    def test(cls, config_name=None, is_export=True, is_update_map=False):
        cfgHelper = ConfigDataHelper(config_name, is_export)
        cfgHelper.init_task_graph()
        cfgHelper.update_topo_device_graph()
        cfgHelper.update_task_map()
        _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        cls._simulate(topo_device_graph, Gd, G_map)
        update_id = 0
        log.info('=== update round {} ==='.format(update_id))
        dev = 'PHONE.0'
        nw_dev = 'BB_AP.0'
        new_nw_dev = 'HOME_IOTGW.0'
        new_latency = Unit.ms(3)
        cfgHelper.update_dev_link(dev, nw_dev, new_nw_dev, new_latency)
        cfgHelper.update_topo_device_graph()
        if is_update_map:
            cfgHelper.update_task_map()
        _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        cls._simulate(topo_device_graph, Gd, G_map)
        # update device graph
        update_id += 1
        log.info('=== update round {} ==='.format(update_id))
        nw_dev1 = 'BB_SWITCH.0'
        nw_dev2 = 'CLOUD_SWITCH.0'
        latency = Unit.sec(5)
        cfgHelper.update_nw_link_latency(nw_dev1, nw_dev2, latency)
        cfgHelper.update_topo_device_graph()
        if is_update_map:
            cfgHelper.update_task_map()
        _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        cls._simulate(topo_device_graph, Gd, G_map)
        # update device graph
        update_id += 1
        log.info('=== update round {} ==='.format(update_id))
        dev = 'PHONE.0'
        nw_dev = 'HOME_IOTGW.0'
        new_nw_dev = 'BB_AP.0'
        new_latency = Unit.ms(3)
        cfgHelper.update_dev_link(dev, nw_dev, new_nw_dev, new_latency)
        cfgHelper.update_topo_device_graph()
        if is_update_map:
            cfgHelper.update_task_map()
        _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        cls._simulate(topo_device_graph, Gd, G_map)
