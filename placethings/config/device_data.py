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


def get_default_inventory(device_spec):
    log.info('create default device inventory')
    device_inventory = default_def.DEVICE_INVENTORY
    # validate the inventory
    assert Validator.validate_inventory(device_spec, device_inventory)
    return device_inventory


def create_default_device_data():
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
                # copy hardware spec
                spec = device_spec[device_cat][device_type]
                device_info = {
                    GdInfo.DEVICE_CAT: device_cat,
                    GdInfo.DEVICE_TYPE: device_type,
                    GdInfo.COST: spec[GdInfo.COST],
                    GdInfo.HARDWARE: spec[GdInfo.HARDWARE],
                    GdInfo.NIC: deepcopy(spec[GdInfo.NIC]),
                    # TODO: bandwidth is a resource
                    GdInfo.RESRC: deepcopy(spec[GdInfo.HARDWARE]),
                }
                # special setting for RESRC info of GPU/CPU
                for hw_type in [Hardware.CPU, Hardware.GPU]:
                    if hw_type in device_info[GdInfo.RESRC]:
                        device_info[GdInfo.RESRC][hw_type] = (
                            Unit.percentage(100))
                all_device_info[device_name] = device_info
    return all_device_info


def export_data():
    device_spec, device_inventory = create_default_device_data()
    filename = common_utils.get_file_path('config_default/device_data.json')
    json_utils.export_bundle(
        filename,
        device_spec=device_spec,
        device_inventory=device_inventory,
    )
    _device_spec, _device_inventory = import_data()
    assert _device_spec == device_spec
    assert _device_inventory == device_inventory


def import_data():
    filename = common_utils.get_file_path('config_default/device_data.json')
    device_spec, device_inventory = json_utils.import_bundle(
        filename,
        'device_spec',
        'device_inventory',
    )
    return device_spec, device_inventory
