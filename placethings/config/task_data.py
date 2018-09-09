from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config import default_def
from placethings.utils import common_utils, json_utils


log = logging.getLogger()


def _get_default_task_mapping():
    return default_def.TASK_MAPPING


def _get_default_task_links():
    return default_def.TASK_LINKS


def _get_default_task_info():
    return default_def.TASK_INFO


def create_default_task_data():
    task_mapping = _get_default_task_mapping()
    task_links = _get_default_task_links()
    task_info = _get_default_task_info()
    return task_mapping, task_links, task_info


_DEFAULT_FILE_PATH = 'config_default/task_data.json'


def export_data():
    task_mapping, task_links, task_info = create_default_task_data()
    filename = common_utils.get_file_path(_DEFAULT_FILE_PATH)
    json_utils.export_bundle(
        filename,
        task_mapping=task_mapping,
        task_links=task_links,
        task_info=task_info,
    )
    _1, _2, _3 = import_data()
    assert _1 == task_mapping
    assert _2 == task_links
    assert _3 == task_info


def import_data(filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH)
    task_mapping, task_links, task_info = json_utils.import_bundle(
        filename,
        'task_mapping',
        'task_links',
        'task_info',
    )
    return task_mapping, task_links, task_info
