from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy

from future.utils import iteritems

from placethings.definition import Device, Flavor, Hardware, GtInfo


class TaskMapping:
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
    def __init__(self):
        self.data = {}

    def get_data(self):
        return self.data

    def add_task(self, task):
        self.data[task] = None

    def add_mapping(self, task, device, device_list):
        assert task in self.data
        assert device in device_list
        self.data[task] = device


class TaskLinks:
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
    def __init__(self):
        self.data = {}

    def get_data(self):
        return self.data

    def add_item(self, src, dst, traffic, task_info_dict):
        """
        only support single direction link.
        args:
            src, dst (str): task name
            traffic (int): e.g. Unit.byte(1)
        """
        assert src in task_info_dict
        assert dst in task_info_dict
        assert type(traffic) is int

        link_name = '{} -> {}'.format(src, dst)
        assert link_name not in self.data
        self.data[link_name] = {
            GtInfo.TRAFFIC: traffic,
        }


class TaskInfo:
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
    def __init__(self):
        self.data = {}

    def get_data(self):
        return self.data

    def add_task(self, task_name):
        """
        args:
            task_name (str)
        """
        assert task_name not in self.data
        self.data[task_name] = {
            GtInfo.LATENCY_INFO: {},
            GtInfo.RESRC_RQMT: {},
        }

    def add_flavor(self, task_name, flavor, resrc_rqmt_dict, latency_dict):
        """
        args:
            task_name (str)
            flavor (Flavor): Flavor.GPU, Flavor.CPU
            resrc_rqmt_dict: e.g. {
                Hardware.RAM: Unit.gbyte(1),
                Hardware.HD: Unit.mbyte(30),
                Hardware.GPU: Unit.percentage(0),
                Hardware.CPU: Unit.percentage(60),
            }
            latency_dict: e.g. {
                Device.T2_MICRO: Unit.sec(6),
                Device.T3_LARGE: Unit.sec(2),
                Device.P3_2XLARGE: Unit.ms(600),
            }
        """
        assert task_name in self.data
        assert type(flavor) is Flavor
        assert flavor not in self.data[task_name][GtInfo.LATENCY_INFO]
        assert flavor not in self.data[task_name][GtInfo.RESRC_RQMT]

        for resrc, value in iteritems(resrc_rqmt_dict):
            assert type(resrc) is Hardware
            assert type(value) is int

        for device_type, latency in iteritems(latency_dict):
            assert type(device_type) is Device
            assert type(latency) is int

        self.data[task_name][GtInfo.RESRC_RQMT][flavor] = (
            copy.deepcopy(resrc_rqmt_dict))

        for device_type, latency in iteritems(latency_dict):
            if device_type in self.data[task_name][GtInfo.LATENCY_INFO]:
                assert flavor not in (
                    self.data[task_name][GtInfo.LATENCY_INFO][device_type])
            else:
                self.data[task_name][GtInfo.LATENCY_INFO][device_type] = {}
            self.data[task_name][GtInfo.LATENCY_INFO][device_type][flavor] = (
                latency)


class AllTaskData(object):
    def __init__(self):
        self.task_mapping = TaskMapping()
        self.task_links = TaskLinks()
        self.task_info = TaskInfo()

    def add_task(self, task_name):
        self.task_info.add_task(task_name)
        self.task_mapping.add_task(task_name)

    def add_flavor(self, task_name, flavor, resrc_rqmt_dict, latency_dict):
        self.task_info.add_flavor(
            task_name, flavor, resrc_rqmt_dict, latency_dict)

    def add_link(self, src, dst, traffic):
        self.task_links.add_item(src, dst, traffic, self.task_info.get_data())

    def add_mapping(self, task, device, device_list):
        self.task_mapping.add_item(task, device, device_list)
