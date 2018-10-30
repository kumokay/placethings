from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time
import random

from placethings.netgen.network import ControlPlane, DataPlane
from placethings.definition import Unit
from placethings.demo.utils import ConfigDataHelper
from placethings.demo.base_test import BaseTestCase


log = logging.getLogger()

"""
network settings

CONTROLLER.0 P3_2XLARGE.0  T3_LARGE.0
       |       |              |
  CENTER_SWITCH.0      FIELD_SWITCH.1      (manager)      T2_MICRO.0
        |                  |                 |               |
    BB_SWITCH.0 ------ BB_SWITCH.1 ---- BB_SWITCH.2 ----FIELD_SWITCH.0
        |                  |                 |
     BB_AP.0             BB_AP.1         BB_AP.2
        |
     CAMERA.0


Drone1 ====flying path================>
Drone2 (standby)

Latency:
  all wired link: 2 ms
  except AP -> SW: 30 ms

Scenrios:
(1) all links alive
(2) P3.X2LARGE.0 offline
(3) T3.XLARGE.0 offline
(4) P3.X2LARGE.0 back online

"""


def _check_support_config(config_name):
    _SUPPORTED_CONFIG = {
        "config_ddflow_demo",
    }
    assert config_name in _SUPPORTED_CONFIG


def _init_netsim(topo_device_graph, Gd, G_map):
    # simulate network
    control_plane = None
    # control_plane = ControlPlane(topo_device_graph)
    # control_plane.add_manager('BB_SWITCH.2')
    # control_plane.deploy_agent()
    # control_plane.runAgent()
    data_plane = DataPlane(topo_device_graph)
    data_plane.add_manager('BB_SWITCH.2')
    data_plane.deploy_task(G_map, Gd)
    return control_plane, data_plane


class TestBasic(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=True, is_simulate=False):
        _check_support_config(config_name)
        cfgHelper = ConfigDataHelper(config_name, is_export)
        cfgHelper.init_task_graph()
        cfgHelper.update_topo_device_graph()
        cfgHelper.update_task_map()
        _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        # simulate
        if is_simulate:
            control_plane, data_plane = _init_netsim(
                topo_device_graph, Gd, G_map)
            # cleanup
            data_plane.start(is_validate=True)
            data_plane.stop()


class TestDynamic(BaseTestCase):

    @classmethod
    def test(
            cls, config_name=None, is_export=True,
            is_update_map=False, is_simulate=False):
        _check_support_config(config_name)
        cfgHelper = ConfigDataHelper(config_name, is_export)
        cfgHelper.init_task_graph()
        cfgHelper.update_topo_device_graph()
        cfgHelper.update_task_map()
        cfgHelper.update_max_latency_log()
        # scenarios:
        # (1) initial deployment, all links are alive
        # (2) P3.X2LARGE.0 poor connection
        # (3) T3.XLARGE.0 poor connection
        # (4) P3.X2LARGE.0 back online
        input('press any key to start scenario 1')
        log.info('=== running scenario 1: initial deployment ===')
        _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        if is_simulate:
            _control_plane, data_plane = _init_netsim(
                topo_device_graph, Gd, G_map)
            data_plane.start(is_validate=True)
        input('press any key to start scenario 2')
        log.info('=== running scenario 2: P3_2XLARGE.0 poor connection ===')
        dev = 'P3_2XLARGE.0'
        nw_dev = 'CENTER_SWITCH.0'
        new_latency = Unit.ms(5000)
        cfgHelper.update_dev_link_latency(dev, nw_dev, new_latency)
        cfgHelper.update_topo_device_graph()
        if is_update_map:
            cfgHelper.update_task_map()
        cfgHelper.update_max_latency_log()
        if is_simulate:
            _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
            data_plane.stop()
            _control_plane, data_plane = _init_netsim(
                topo_device_graph, Gd, G_map)
            data_plane.start(is_validate=False)
        input('press any key to start scenario 3')
        log.info('=== running scenario 3: T3_LARGE.0 poor connection ===')
        dev = 'T3_LARGE.0'
        nw_dev = 'FIELD_SWITCH.1'
        new_latency = Unit.ms(5000)
        cfgHelper.update_dev_link_latency(dev, nw_dev, new_latency)
        cfgHelper.update_topo_device_graph()
        if is_update_map:
            cfgHelper.update_task_map()
        cfgHelper.update_max_latency_log()
        if is_simulate:
            _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
            data_plane.stop()
            _control_plane, data_plane = _init_netsim(
                topo_device_graph, Gd, G_map)
            data_plane.start(is_validate=False)
        input('press any key to start scenario 4')
        log.info('=== running scenario 4: P3_2XLARGE.0 back online ===')
        dev = 'P3_2XLARGE.0'
        nw_dev = 'CENTER_SWITCH.1'
        new_latency = Unit.ms(2)
        cfgHelper.update_dev_link_latency(dev, nw_dev, new_latency)
        cfgHelper.update_topo_device_graph()
        if is_update_map:
            cfgHelper.update_task_map()
        cfgHelper.update_max_latency_log()
        _topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        if is_simulate:
            data_plane.stop()
            _control_plane, data_plane = _init_netsim(
                topo_device_graph, Gd, G_map)
            data_plane.start(is_validate=False)
        input('press any key to end test')
        if is_simulate:
            data_plane.stop()
        log.info('latency trend: {}'.format(cfgHelper.get_max_latency_log()))
