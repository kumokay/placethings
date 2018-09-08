from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import range
from copy import deepcopy
from future.utils import iteritems
import logging

from placethings.definition import (
    Const, Device, DeviceCategory, Flavor, GtInfo, GdInfo, GnInfo,
    Hardware, NetworkDevice, NetworkLink, Unit)
from placethings.utils import json_utils, common_utils


log = logging.getLogger()



def _create_default_deployment(nw_device_spec, device_inventory):
    log.info('create default deployment')
    nw_devices = SetManager(set(nw_device_spec))
    inventory = InventoryManager(device_inventory)
    # TODO: use dict and add latency & bandwidth
    links = []
    # attach devices to HomeIotGW
    network_device = nw_devices.get('HomeIotGW')
    device = inventory.pop(DeviceCategory.SENSOR, Device.THERMAL)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.SENSOR, Device.THERMAL)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.SENSOR, Device.CAMERA)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    # attach devices to HomeRouter
    network_device = nw_devices.get('HomeRouter')
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.T2_MICRO)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.T3_LARGE)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    # attach devices to CloudSwitch
    network_device = nw_devices.get('CloudSwitch')
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.T2_MICRO)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.T3_LARGE)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.P3_2XLARGE)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    # attach devices to BaseStation
    network_device = nw_devices.get('BaseStation')
    device = inventory.pop(DeviceCategory.ACTUATOR, Device.PHONE)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    return links





def export_all_data():
    device_spec, device_inventory = create_default_device_data()
    json_utils.export_bundle(
        'config_default/device_data.json',
        device_spec=device_spec,
        device_inventory=device_inventory)
    _device_spec, _device_inventory = json_utils.import_bundle(
        common_utils.get_file_path('config_default/device_data.json'),
        'device_spec',
        'device_inventory',
    )
    assert _device_spec == device_spec
    assert _device_inventory == device_inventory

    task_info, edge_info, src_map, dst_map = create_default_task_graph()
    json_utils.export_bundle(
        common_utils.get_file_path('config_default/task_graph.json'),
        task_info=task_info,
        edge_info=edge_info,
        src_map=src_map,
        dst_map=dst_map,
    )
    _task_info, _edge_info, _src_map, _dst_map = json_utils.import_bundle(
        common_utils.get_file_path('config_default/task_graph.json'),
        'task_info',
        'edge_info',
        'src_map',
        'dst_map',
    )
    assert _task_info == task_info
    assert _edge_info == edge_info
    assert _src_map == src_map, (
        '\n{}\n!=\n{}'.format(_src_map, src_map))
    assert _dst_map == dst_map

    nw_device_spec, nw_links, device_links = create_default_topo()
    json_utils.export_bundle(
        common_utils.get_file_path('config_default/topo.json'),
        nw_device_spec=nw_device_spec,
        nw_links=nw_links,
        device_links=device_links,
    )
    _nw_device_spec, _nw_links, _device_links = json_utils.import_bundle(
        common_utils.get_file_path('config_default/topo.json'),
        'nw_device_spec',
        'nw_links',
        'device_links',
    )
    assert _nw_device_spec == nw_device_spec
    assert _nw_links == nw_links
    assert _device_links == device_links
