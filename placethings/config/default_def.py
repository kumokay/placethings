from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from placethings.definition import (
    Device, DeviceCategory, NwDevice, NwDeviceCategory)
from placethings.utils import json_utils, common_utils


NW_DEVICE_INVENTORY = {
    NwDeviceCategory.HOME: {
        NwDevice.HOME_ROUTER: 1,
        NwDevice.HOME_IOTGW: 1,
    },
    NwDeviceCategory.BACKBONE: {
        NwDevice.BB_SWITCH: 1,
        NwDevice.BASESTATION: 1,
    },
    NwDeviceCategory.CLOUD: {
        NwDevice.CLOUD_SWITCH: 1,
    },
}


DEVICE_INVENTORY = {
    DeviceCategory.ACTUATOR: {
        Device.PHONE: 1,
    },
    DeviceCategory.PROCESSOR: {
        Device.T2_MICRO: 2,
        Device.T3_LARGE: 2,
        Device.P3_2XLARGE: 1,
    },
    DeviceCategory.SENSOR: {
        Device.THERMAL: 2,
        Device.CAMERA: 1,
    },
}


DEFAULT_TASKS = [
    'task_thermal_loc1',
    'task_thermal_loc2',
    'task_camera',
    'task_broadcast',
    'task_getAvgTemperature',
    'task_findObject',
    'task_checkAbnormalEvent',
    'task_sentNotificatoin',
]


# device naming rule: DeviceTypeName.ID
DEFAULT_MAPPING = {
    'task_thermal_loc1': 'THERMAL.0',
    'task_thermal_loc2': 'THERMAL.1',
    'task_camera': 'CAMERA.0',
    'task_broadcast': 'PHONE.0',
}


def export_data():
    filename = common_utils.get_file_path('config_default/nw_device_data.json')
    json_utils.export_bundle(
        filename,
        NW_DEVICE_INVENTORY=NW_DEVICE_INVENTORY,
        DEVICE_INVENTORY=DEVICE_INVENTORY,
        DEFAULT_TASKS=DEFAULT_TASKS,
        DEFAULT_MAPPING=DEFAULT_MAPPING,
    )
    _1, _2, _3, _4 = json_utils.import_bundle(
        filename,
        'NW_DEVICE_INVENTORY',
        'DEVICE_INVENTORY',
        'DEFAULT_TASKS',
        'DEFAULT_MAPPING',
    )
    assert _1 == NW_DEVICE_INVENTORY
    assert _2 == DEVICE_INVENTORY
    assert _3 == DEFAULT_TASKS
    assert _4 == DEFAULT_MAPPING
