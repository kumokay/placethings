from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from placethings.config.wrapper.device_gen import AllDeviceData
from placethings.config.wrapper.task_gen import AllTaskData
from placethings.config import spec_def


class Config(object):
    def __init__(self):
        self.all_device_data = AllDeviceData()
        self.all_task_data = AllTaskData()
        self.DEVICE_SPEC = spec_def.DEVICE_SPEC
        self.NW_DEVICE_SPEC = spec_def.NW_DEVICE_SPEC

    def add_device(self, device_category, device, num):
        assert device_category in self.DEVICE_SPEC
        assert device in self.DEVICE_SPEC[device_category]
        self.all_device_data.add_device(device_category, device, num)

    def add_nw_device(self, nw_device_category, nw_device, num):
        assert nw_device_category in self.NW_DEVICE_SPEC
        assert nw_device in self.NW_DEVICE_SPEC[nw_device_category]
        self.all_device_data.add_nw_device(nw_device_category, nw_device, num)

    def add_dev_link(self, dev, nw_dev, latency):
        self.all_device_data.add_dev_link(dev, nw_dev, latency)

    def add_nw_dev_link(self, src, dst, src_link_type, dst_link_type, latency):
        self.all_device_data.add_nw_dev_link(
            src, dst, src_link_type, dst_link_type, latency)

    def add_task(self, task_name):
        self.all_task_data.add_task(task_name)

    def add_task_flavor(
            self, task_name, flavor, resrc_rqmt_dict, latency_dict):
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
        self.all_task_data.add_flavor(
            task_name, flavor, resrc_rqmt_dict, latency_dict)

    def add_task_link(self, src, dst, traffic):
        self.all_task_data.add_link(src, dst, traffic)

    def add_task_mapping(self, task, device):
        device_list = self.all_device_data.device_inventory.get_device_list()
        self.all_task_data.add_mapping(task, device, device_list)
