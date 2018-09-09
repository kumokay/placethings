from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import iteritems
import logging

from placethings.config import default_def, device_data, task_graph
from placethings.config.common import Validator
from placethings.utils import common_utils, json_utils


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
    Gt = task_graph.create_default_task_graph()
    _device_spec, device_inventory = device_data.create_default_device_data()
    # create mapping
    task_set = set(Gt)
    known_mapping = default_def.DEFAULT_MAPPING
    assert Validator.validate_mapping(
        task_set, device_inventory, known_mapping)
    return create_mapping(task_set, known_mapping)


def export_data():
    default_map = create_default_mapping()
    filename = common_utils.get_file_path('config_default/default_map.json')
    json_utils.export_bundle(
        filename,
        default_map=default_map,
    )
    _1, = json_utils.import_bundle(
        filename,
        'default_map',
    )
    assert _1 == default_map
