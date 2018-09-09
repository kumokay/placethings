from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy
from future.utils import iteritems
import logging

from placethings.config import default_def, spec_def
from placethings.config.common import InventoryManager, Validator
from placethings.definition import GdInfo, Hardware, Unit
from placethings.utils import common_utils, json_utils


log = logging.getLogger()


def get_default_spec():
    return spec_def.DEVICE_SPEC


def get_default_links():
    return default_def.DEVICE_LINKS


def get_default_inventory(device_spec):
    log.info('create default device inventory')
    device_inventory = default_def.DEVICE_INVENTORY
    # validate the inventory
    assert Validator.validate_inventory(device_spec, device_inventory)
    return device_inventory


def create_default_device_data():
    device_spec = get_default_spec()
    device_inventory = get_default_inventory(device_spec)
    links = get_default_links()
    return device_spec, device_inventory, links


def get_device_data(filepath):
    device_spec, device_inventory, links = import_data(filepath)
    return device_spec, device_inventory, links


_DEFAULT_FILE_PATH = 'config_default/device_data.json'


def export_data():
    filename = common_utils.get_file_path(_DEFAULT_FILE_PATH)
    device_spec, device_inventory, links = create_default_device_data()
    json_utils.export_bundle(
        filename,
        device_spec=device_spec,
        device_inventory=device_inventory,
        links=links,
    )
    _1, _2, _3 = import_data()
    assert _1 == device_spec
    assert _2 == device_inventory
    assert _3 == links


def import_data(filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH)
    device_spec, device_inventory, links = json_utils.import_bundle(
        filename,
        'device_spec',
        'device_inventory',
        'links',
    )
    return device_spec, device_inventory, links
