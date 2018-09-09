from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config import device_data, nw_device_data, task_data
from placethings.utils import common_utils


log = logging.getLogger()


def export_default_config():
    device_data.export_data()
    nw_device_data.export_data()
    task_data.export_data()


def import_all_config(config_name):
    filename = 'device_data.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    device_spec, device_inventory, links = device_data.import_data(filepath)
    device_data_set = (device_spec, device_inventory, links)
    filename = 'nw_device_data.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    nw_spec, nw_inventory, nw_links = nw_device_data.import_data(filepath)
    nw_data_set = (nw_spec, nw_inventory, nw_links)
    filename = 'task_data.json'
    filepath = common_utils.get_config_filepath(config_name, filename)
    mapping, task_links, task_info = task_data.import_data(filepath)
    task_data_set = (mapping, task_links, task_info)
    return device_data_set, nw_data_set, task_data_set
