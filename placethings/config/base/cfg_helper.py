from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import iteritems

from placethings.config.base import device_cfg, mapping_cfg, task_cfg


class ConfigHelper(object):
    def __init__(self, device_data=None, task_data=None, mapping_data=None):
        if not device_data:
            device_data = device_cfg.DeviceData()
        if not task_data:
            task_data = task_cfg.TaskData()
        if not mapping_data:
            mapping_data = mapping_cfg.MappingData()
        assert type(device_data) == device_cfg.DeviceData
        assert type(task_data) == task_cfg.TaskData
        assert type(mapping_data) == mapping_cfg.MappingData

        # validate
        for task_id, device_id in iteritems(mapping_data.get_mapping_dict()):
            assert task_data.has_task(task_id)
            if device_id != 'null':
                assert device_data.has_device(device_id)
        for task_id in task_data.get_task_dict():
            assert mapping_data.has_task(task_id)

        self.device_data = device_data
        self.task_data = task_data
        self.mapping_data = mapping_data

    def export_to_file(self, folder_path):
        self.device_data.export_to_file(
            '{}/device_data.json'.format(folder_path))
        self.task_data.export_to_file(
            '{}/task_data.json'.format(folder_path))
        self.mapping_data.export_to_file(
            '{}/mapping_data.json'.format(folder_path))

    def import_from_file(self, folder_path):
        self.device_data.import_from_file(
            '{}/device_data.json'.format(folder_path))
        self.task_data.import_from_file(
            '{}/task_data.json'.format(folder_path))
        self.mapping_data.import_from_file(
            '{}/mapping_data.json'.format(folder_path))
        return self
