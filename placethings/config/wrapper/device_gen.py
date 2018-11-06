from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy

from future.utils import iteritems

from placethings.definition import (
    Device, DeviceCategory, Flavor, Hardware, NwDevice, NwDeviceCategory,
    GnInfo, GtInfo, LinkType, Unit)


class NwDeviceInventory:
    """ wrapper for
        NW_DEVICE_INVENTORY = {
            NwDeviceCategory.HOME: {
                NwDevice.HOME_ROUTER: 1,
                NwDevice.HOME_IOTGW: 1,
            },
            NwDeviceCategory.BACKBONE: {
                NwDevice.BB_SWITCH: 1,
                NwDevice.BB_AP: 1,
            },
            NwDeviceCategory.CLOUD: {
                NwDevice.CLOUD_SWITCH: 1,
            },
        }
    """
    def __init__(self):
        self.data = {}

    def get_data(self):
        return self.data

    def get_device_list(self):
        device_list = []
        for cat, cat_data in iteritems(self.data):
            for dev_type, dev_cnt in iteritems(cat_data):
                for i in range(dev_cnt):
                    _classname, dev_type_short = str(dev_type).split('.')
                    dev_name = '{}.{}'.format(dev_type_short, i)
                    device_list.append[dev_name]
        return device_list

    def add_item(self, nw_device_category, nw_device, num):
        """
        args:
            nw_device_category (NwDeviceCategory): e.g. NwDeviceCategory.HOME
            nw_device (NwDevice): e.g. NwDeviceCategory.BACKBONE
            num (int): how many devices
        """
        assert type(nw_device_category) is NwDeviceCategory
        assert type(nw_device) is NwDevice
        if nw_device_category not in self.data:
            self.data[nw_device_category] = {}
        assert nw_device not in self.data[nw_device_category]
        self.data[nw_device_category][nw_device] = num


class NwLinks:
    """ wrapper for
        NW_LINKS = {
            'HOME_IOTGW.0 -> HOME_ROUTER.0': {
                GnInfo.SRC_LINK_TYPE: LinkType.WAN,
                GnInfo.DST_LINK_TYPE: LinkType.LAN,
                GnInfo.LATENCY: Unit.ms(1),
            },
            'HOME_ROUTER.0 -> HOME_IOTGW.0': {
                GnInfo.SRC_LINK_TYPE: LinkType.LAN,
                GnInfo.DST_LINK_TYPE: LinkType.WAN,
                GnInfo.LATENCY: Unit.ms(1),
            },
            ...
            'CLOUD_SWITCH.0 -> BB_SWITCH.0': {
                GnInfo.SRC_LINK_TYPE: LinkType.WAN,
                GnInfo.DST_LINK_TYPE: LinkType.ANY,
                GnInfo.LATENCY: Unit.ms(15),
            },
            'BB_SWITCH.0 -> CLOUD_SWITCH.0': {
                GnInfo.SRC_LINK_TYPE: LinkType.ANY,
                GnInfo.DST_LINK_TYPE: LinkType.WAN,
                GnInfo.LATENCY: Unit.ms(15),
            }
        }
    """
    def __init__(self):
        self.data = {}

    def get_data(self):
        return self.data

    def add_item(
            self, src, dst, src_link_type, dst_link_type, latency,
            nw_devic_list):
        """
        only support balanced link.
        args:
            src, dst (str)
            src_link_type, dst_link_type (LinkType)
            latency (int)
            nw_devic_list (list)
        """
        assert src in nw_device_list
        assert dst in nw_device_list
        assert type(src_link_type) is LinkType
        assert type(dst_link_type) is LinkType
        assert type(latency) is int

        link_name = '{} -> {}'.format(src, dst)
        assert link_name not in self.data
        self.data[link_name] = {
            GnInfo.SRC_LINK_TYPE: src_link_type,
            GnInfo.DST_LINK_TYPE: dst_link_type,
            GnInfo.LATENCY: latency,
        }

        link_name = '{} -> {}'.format(dst, src)
        assert link_name not in self.data
        self.data[link_name] = {
            GnInfo.SRC_LINK_TYPE: dst_link_type,
            GnInfo.DST_LINK_TYPE: src_link_type,
            GnInfo.LATENCY: latency,
        }


class DeviceInventory:
    """ wrapper for
        DEVICE_INVENTORY = {
            DeviceCategory.ACTUATOR: {
                Device.PHONE: 1,
            },
            DeviceCategory.PROCESSOR: {
                Device.T2_MICRO: 2,
                Device.T3_LARGE: 2,
                Device.P3_2XLARGE: 1,
            },
            DeviceCategory.SENSOR: {
                Device.SMOKE: 1,
                Device.CAMERA: 1,
            },
        }
    """
    def __init__(self):
        self.data = {}

    def get_data(self):
        return self.data

    def get_device_list(self):
        device_list = []
        for cat, cat_data in iteritems(self.data):
            for dev_type, dev_cnt in iteritems(cat_data):
                for i in range(dev_cnt):
                    _classname, dev_type_short = str(dev_type).split('.')
                    dev_name = '{}.{}'.format(dev_type_short, i)
                    device_list.append[dev_name]
        return device_list

    def add_item(self, device_category, device, num):
        """
        args:
            device_category (DeviceCategory): e.g. DeviceCategory.PROCESSOR
            device (Device): e.g. Device.T2_MICRO
            num (int): how many devices
        """
        assert type(device_category) is NwDeviceCategory
        assert type(device) is NwDevice
        if device_category not in self.data:
            self.data[device_category] = {}
        assert device not in self.data[device_category]
        self.data[device_category][device] = num


class DeviceLinks:
    """ a wrapper for
        DEVICE_LINKS = {
            'SMOKE.0 -> HOME_IOTGW.0': {
                GnInfo.LATENCY: Unit.ms(3),
            },
            'CAMERA.0 -> HOME_IOTGW.0': {
                GnInfo.LATENCY: Unit.ms(3),
            },
            ...
            'PHONE.0 -> BB_AP.0': {
                GnInfo.LATENCY: Unit.ms(10),
            },
            'BB_AP.0 -> PHONE.0': {
                GnInfo.LATENCY: Unit.ms(10),
            },
        }
        """
    def __init__(self):
        self.data = {}

    def get_data(self):
        return self.data

    def add_item(self, dev, nw_dev, latency, device_list, nw_device_list):
        """
        only support balanced link.
        args:
            dev, nw_dev (str)
            latency (int)
            device_list, nw_device_list (list)
        """
        assert dev in device_list
        assert nw_dev in nw_device_list
        assert type(latency) is int

        link_name = '{} -> {}'.format(dev, nw_dev)
        assert link_name not in self.data
        self.data[link_name] = {
            GnInfo.LATENCY: latency,
        }

        link_name = '{} -> {}'.format(nw_dev, dev)
        assert link_name not in self.data
        self.data[link_name] = {
            GnInfo.LATENCY: latency,
        }


class AllDeviceData(object):
    def __init__(self):
        self.device_inventory = DeviceInventory()
        self.nw_device_inventory = NwDeviceInventory()
        self.device_links = DeviceLinks()
        self.nw_device_links = NwDeviceLinks()

    def add_device(self, device_category, device, num):
        self.device_inventory.add_item(device_category, device, num)

    def add_nw_device(self, nw_device_category, nw_device, num):
        self.nw_device_inventory.add_item(nw_device_category, nw_device, num)

    def add_dev_link(self, dev, nw_dev, latency):
        device_list = self.device_inventory.get_device_list()
        nw_device_list = self.nw_device_inventory.get_device_list()
        device_links.add_item(dev, nw_dev, latency, device_list, nw_device_list)

    def add_nw_dev_link(self, src, dst, src_link_type, dst_link_type, latency):
        nw_device_list = self.nw_device_inventory.get_device_list()
        device_links.add_item(
            src, dst, src_link_type, dst_link_type, latency,
            nw_device_list)
