from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy
from future.utils import iteritems
import logging

from placethings.config import default_def, spec_def
from placethings.config.common import InventoryManager, Validator
from placethings.definition import GnInfo


log = logging.getLogger()


def get_default_spec():
    return spec_def.NW_DEVICE_SPEC


def get_default_inventory(device_spec):
    log.info('create default nw device inventory')
    device_inventory = default_def.NW_DEVICE_INVENTORY
    # validate the inventory
    assert Validator.validate_inventory(device_spec, device_inventory)
    return device_inventory


def create_default_device_data():
    """
    Returns:
        device_spec
        device_inventory
    """
    device_spec = get_default_spec()
    device_inventory = get_default_inventory(device_spec)
    return device_spec, device_inventory


def derive_device_info(device_spec, device_inventory):
    all_device_info = {}
    inventory_manager = InventoryManager(device_inventory)
    device_record = inventory_manager.get_device_record()
    for device_cat, inventory_info in iteritems(device_record):
        for device_type, device_list in iteritems(inventory_info):
            for device_name in device_list:
                # copy link spec
                link_spec_dict = device_spec[device_cat][device_type]
                device_info = {
                    GnInfo.DEVICE_CAT: device_cat,
                    GnInfo.DEVICE_TYPE: device_type,
                    GnInfo.LINK_INFO: deepcopy(link_spec_dict),
                }
                all_device_info[device_name] = device_info
    return all_device_info
