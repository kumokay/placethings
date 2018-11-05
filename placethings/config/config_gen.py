from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import iteritems

from placethings.definition import (
    Device, DeviceCategory, Flavor, Hardware, NwDevice, NwDeviceCategory,
    GnInfo, GtInfo, LinkType, Unit)


""" generate config by code. this is just a wrapper
"""


def validate_device_name(name):
    """
    Args:
        name (str): e.g. CLOUD_SWITCH.0, T2_MICRO.1
    Return:
        is_valid (bool)
    """
    # TODO: check seq_no
    type, seq_no = name.split('.')
    return hasattr(NwDevice, name) or hasattr(Device, name)


class C_NW_DEVICE_INVENTORY:
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


class C_NW_LINKS:
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
    def __init__(self, nw_devic_list):
        self.data = {}
        self.nw_device_list = nw_devic_list

    def get_data(self):
        return self.data

    def add_item(self, src, dst, src_link_type, dst_link_type, latency):
        """
        only support balanced link.
        args:
            src, dst (str)
            src_link_type, dst_link_type (LinkType)
            latency(link)
        """
        assert src in self.nw_device_list
        assert dst in self.nw_device_list
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


class C_DEVICE_INVENTORY:
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


class C_DEVICE_LINKS:
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
    def __init__(self, device_list):
        self.data = {}
        self.device_list = device_list

    def get_data(self):
        return self.data

    def add_item(self, src, dst, latency):
        """
        only support balanced link.
        args:
            src, dst (str)
            src_link_type, dst_link_type (LinkType)
            latency(link)
        """
        assert src in self.nw_device_list
        assert dst in self.nw_device_list
        assert type(latency) is int

        link_name = '{} -> {}'.format(src, dst)
        assert link_name not in self.data
        self.data[link_name] = {
            GnInfo.LATENCY: latency,
        }

        link_name = '{} -> {}'.format(dst, src)
        assert link_name not in self.data
        self.data[link_name] = {
            GnInfo.LATENCY: latency,
        }


class C_TASK_MAPPING:
    """
    Wrapper for
        TASK_MAPPING = {
            'task_smoke': 'SMOKE.0',
            'task_camera': 'CAMERA.0',
            'task_broadcast': 'PHONE.0',
            'task_getAvgReading': None,
            'task_findObject': None,
            'task_checkAbnormalEvent': None,
            'task_sentNotificatoin': None,
        }
    """
    def __init__(self, task_info, device_list):
        self.data = {}
        self.task_info = task_info
        self.device_list = device_list

    def get_data(self):
        return self.data

    def add_item(self, task, device):
        assert task in self.task_info
        assert device is None or device in self.device_list
        assert task not in self.data
        self.data[task] = device


class C_TASK_LINKS:
    """
    Wrapper for
        TASK_LINKS = {
            'task_smoke -> task_getAvgReading': {
                GtInfo.TRAFFIC: Unit.kbyte(1),
            },
            ...
            'task_sentNotificatoin -> task_broadcast': {
                GtInfo.TRAFFIC: Unit.byte(1),
            },
        }
    """
    def __init__(self, task_info):
        self.data = {}
        self.task_info = task_info

    def get_data(self):
        return self.data

    def add_item(self, src, dst, traffic):
        """
        only support single direction link.
        args:
            src, dst (str): task name
            traffic (int): e.g. Unit.byte(1)
        """
        assert src in self.task_info
        assert dst in self.task_info
        assert type(traffic) is int

        link_name = '{} -> {}'.format(src, dst)
        assert link_name not in self.data
        self.data[link_name] = {
            GtInfo.TRAFFIC: traffic,
        }


# TODO: write this
class C_TASK_RESRC_RQMT:
    """
    wrapper for
        GtInfo.RESRC_RQMT: {
            Flavor.GPU: {
                Hardware.RAM: Unit.gbyte(4),
                Hardware.HD: Unit.mbyte(30),
                Hardware.GPU: Unit.percentage(60),
                Hardware.CPU: Unit.percentage(5),
            },
            Flavor.CPU: {
                Hardware.RAM: Unit.gbyte(1),
                Hardware.HD: Unit.mbyte(30),
                Hardware.GPU: Unit.percentage(0),
                Hardware.CPU: Unit.percentage(60),
            },
        },
    """

class C_TASK_LATENCY_INFO:
    """
    wrapper for
        GtInfo.LATENCY_INFO: {
            Device.T2_MICRO: {
                Flavor.CPU: Unit.sec(6),
            },
            Device.T3_LARGE: {
                Flavor.CPU: Unit.sec(2),
            },
            Device.P3_2XLARGE: {
                Flavor.GPU: Unit.ms(600),
            },
        }
    """

class C_TASK_INFO:
    """
    wrapper for
        TASK_INFO = {
            'task_camera': {
                GtInfo.LATENCY_INFO: {},
                GtInfo.RESRC_RQMT: {},
            },
            ...
            'task_findObject': {
                GtInfo.LATENCY_INFO: {
                    Device.T2_MICRO: {
                        Flavor.CPU: Unit.sec(6),
                    },
                    Device.T3_LARGE: {
                        Flavor.CPU: Unit.sec(2),
                    },
                    Device.P3_2XLARGE: {
                        Flavor.GPU: Unit.ms(600),
                    },
                },
                GtInfo.RESRC_RQMT: {
                    Flavor.GPU: {
                        Hardware.RAM: Unit.gbyte(4),
                        Hardware.HD: Unit.mbyte(30),
                        Hardware.GPU: Unit.percentage(60),
                        Hardware.CPU: Unit.percentage(5),
                    },
                    Flavor.CPU: {
                        Hardware.RAM: Unit.gbyte(1),
                        Hardware.HD: Unit.mbyte(30),
                        Hardware.GPU: Unit.percentage(0),
                        Hardware.CPU: Unit.percentage(60),
                    },
                },
            },
            ...
        }
    """
