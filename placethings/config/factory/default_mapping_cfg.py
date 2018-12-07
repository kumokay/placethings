from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from placethings.config.base import mapping_cfg


def create_default_mapping_data():
    mapping_data = mapping_cfg.MappingData()
    mapping_data.add_mapping('capture_image', 'patroller_drone')
    mapping_data.add_mapping('detect_object', 'gpu_server')
    mapping_data.add_mapping('send_notification', 'samsung_phone')

    return mapping_data
