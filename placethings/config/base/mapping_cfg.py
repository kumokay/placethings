from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import iteritems

from placethings.config.base.serializable import SerializableObject


class MappingData(SerializableObject):
    def __init__(self, mapping_dict=None):
        if not mapping_dict:
            mapping_dict = {}
        assert type(mapping_dict) == dict
        for task_id, device_id in iteritems(mapping_dict):
            assert type(task_id) == unicode
            assert type(device_id) == unicode
        self.mapping_dict = mapping_dict

    def has_task(self, task_id):
        return self.mapping_dict[task_id]

    def get_mapping_dict(self):
        return self.mapping_dict

    def add_mapping(self, task_id, device_id):
        assert type(task_id) == unicode
        assert type(device_id) == unicode
        assert task_id not in self.mapping_dict
        self.mapping_dict[task_id] = device_id
