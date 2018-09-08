from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import iteritems
import logging

from placethings.config import default, device_data, task_graph
from placethings.config.common import InventoryManager, Validator


log = logging.getLogger()


def create_mapping(task_set, known_mapping):
    mapping = {}
    for task in task_set:
        mapping[task] = None
    for task, device in iteritems(known_mapping):
        assert task in task_set
        mapping[task] = device
    return mapping


def create_default_mapping():
    task_info, _edge_info = task_graph.create_default_task_graph()
    _device_spec, device_inventory = device_data.create_default_device_data()
    # create mapping
    task_set = set(task_info)
    device_set = InventoryManager(device_inventory).get_device_set()
    known_mapping = default.DEFAULT_MAPPING
    assert Validator.validate_mapping(
        task_info, device_inventory, known_mapping)
    return create_mapping(task_set, device_set, known_mapping)
