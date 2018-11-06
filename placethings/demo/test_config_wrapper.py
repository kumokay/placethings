from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config.wrapper.config_gen import Config
from placethings.demo.base_test import BaseTestCase
from placethings.definition import (
    Device, DeviceCategory, Flavor, Hardware, NwDevice, NwDeviceCategory,
    GnInfo, GtInfo, LinkType, Unit)

log = logging.getLogger()

"""
network settings

CONTROLLER.0   P3_2XLARGE.0     T3_LARGE.0
       |         |                 |
CENTER_SWITCH.1 CENTER_SWITCH.0  FIELD_SWITCH.1   (manager)      T2_MICRO.0
        |       |                 |                 |               |
      BB_SWITCH.0 --------- BB_SWITCH.1 ---- BB_SWITCH.2 ----FIELD_SWITCH.0
        |                    |                 |
     BB_AP.0               BB_AP.1         BB_AP.2
        |
     CAMERA.0
"""


class TestConfigWrapper(BaseTestCase):
    @staticmethod
    def test(config_name=None, is_export=False):
        assert config_name is None
        cfg = Config()

        cfg.add_nw_device(NwDeviceCategory.FIELD, NwDevice.FIELD_SWITCH, 2)
        cfg.add_nw_device(NwDeviceCategory.BACKBONE, NwDevice.BB_SWITCH, 3)
        cfg.add_nw_device(NwDeviceCategory.BACKBONE, NwDevice.BB_AP, 3)
        cfg.add_nw_device(NwDeviceCategory.CENTER, NwDevice.CENTER_SWITCH, 2)

        cfg.add_nw_dev_link(
            'CENTER_SWITCH.1', 'BB_SWITCH.0',
            LinkType.WAN, LinkType.ANY, Unit.ms(2))
        cfg.add_nw_dev_link(
            'CENTER_SWITCH.0', 'BB_SWITCH.0',
            LinkType.WAN, LinkType.ANY, Unit.ms(2))
        cfg.add_nw_dev_link(
            'FIELD_SWITCH.1', 'BB_SWITCH.1',
            LinkType.WAN, LinkType.ANY, Unit.ms(2))
        cfg.add_nw_dev_link(
            'FIELD_SWITCH.1', 'BB_SWITCH.2',
            LinkType.WAN, LinkType.ANY, Unit.ms(2))
        cfg.add_nw_dev_link(
            'BB_AP.0', 'BB_SWITCH.0',
            LinkType.WAN, LinkType.ANY, Unit.ms(2))
        cfg.add_nw_dev_link(
            'BB_AP.1', 'BB_SWITCH.1',
            LinkType.WAN, LinkType.ANY, Unit.ms(2))
        cfg.add_nw_dev_link(
            'BB_AP.2', 'BB_SWITCH.2',
            LinkType.WAN, LinkType.ANY, Unit.ms(2))
        cfg.add_nw_dev_link(
            'BB_SWITCH.0', 'BB_SWITCH.1',
            LinkType.ANY, LinkType.ANY, Unit.ms(2))
        cfg.add_nw_dev_link(
            'BB_SWITCH.1', 'BB_SWITCH.2',
            LinkType.ANY, LinkType.ANY, Unit.ms(2))

        cfg.add_device(DeviceCategory.SENSOR, Device.CAMERA, 1)
        cfg.add_device(DeviceCategory.PROCESSOR, Device.P3_2XLARGE, 1)
        cfg.add_device(DeviceCategory.PROCESSOR, Device.T3_LARGE, 2)
        cfg.add_device(DeviceCategory.PROCESSOR, Device.T2_MICRO, 4)
        cfg.add_device(DeviceCategory.ACTUATOR, Device.CONTROLLER, 1)

        cfg.add_dev_link('CAMERA.0', 'BB_AP.0', Unit.ms(30))
        cfg.add_dev_link('P3_2XLARGE.0', 'CENTER_SWITCH.0', Unit.ms(2))
        cfg.add_dev_link('T3_LARGE.0', 'FIELD_SWITCH.1', Unit.ms(2))
        cfg.add_dev_link('T2_MICRO.0', 'FIELD_SWITCH.0', Unit.ms(2))
        cfg.add_dev_link('CONTROLLER.0', 'CENTER_SWITCH.1', Unit.ms(2))

        # TODO: fuuuu GtInfoEnum.EXEC_CMD
        cfg.add_task()
