from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config import device_data, nw_device_data, topo_graph
from placethings.config.common import LinkHelper, InventoryManager
from placethings.definition import (
    Device, DeviceCategory, GdInfo, GnInfo, LinkType, LinkInfo,
    NwDevice, NwDeviceCategory, Unit)
from placethings.utils import common_utils, graph_utils, json_utils


log = logging.getLogger()


def _create_default_node_info():
    """
    Returns:
        node_info (dict): {node_name (str): node_data (dict)}, where
            node_data = { data_name (GtInfo): data (any) }
    """
    log.info('create default node (device) info')
    device_spec, device_inventory = device_data.create_default_device_data()
    node_info = device_data.derive_device_info(device_spec, device_inventory)
    return node_info


def _get_nw_device_link_info(inventory, name, link_type):
    spec = inventory.get_spec(name)[link_type]
    return (
        spec[LinkInfo.ULINK_BW],
        spec[LinkInfo.DLINK_BW],
        spec[LinkInfo.PROTOCOL])


def _get_device_link_info(inventory, name):
    spec = inventory.get_spec(name)[GdInfo.NIC]
    return (
        spec[LinkInfo.ULINK_BW],
        spec[LinkInfo.DLINK_BW],
        spec[LinkInfo.PROTOCOL])


def _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay):
    ul_dev, dl_dev, prot_dev = _get_device_link_info(device_inventory, device)
    link_type = LinkType.LAN
    ul_nw, dl_nw, prot_nw = _get_nw_device_link_info(
        nw_inventory, nw_device, link_type)
    assert prot_dev == prot_nw
    prot = prot_dev
    edge_info = {}
    edge_info[LinkHelper.get_edge(device, nw_device)] = {
        GnInfo.SRC_LINK_TYPE: link_type,
        GnInfo.DST_LINK_TYPE: link_type,
        GnInfo.BANDWIDTH: min(ul_dev, dl_nw),
        GnInfo.LATENCY: ul_delay,
        GnInfo.PROTOCOL: prot,
    }
    edge_info[LinkHelper.get_edge(nw_device, device)] = {
        GnInfo.SRC_LINK_TYPE: link_type,
        GnInfo.DST_LINK_TYPE: link_type,
        GnInfo.BANDWIDTH: min(ul_nw, dl_dev),
        GnInfo.LATENCY: dl_delay,
        GnInfo.PROTOCOL: prot,
    }
    return edge_info


def _create_default_edge_info():
    """
    Returns:
        edge_info (dict): { 'node1 -> node2' (str): edge_data (dict)}, where
            edge_data = { data_name (GtInfo): data (any) }
    """
    log.info('create default edge (link) info')
    # get nw devices
    nw_device_spec, nw_device_inventory = (
        nw_device_data.create_default_device_data())
    nw_inventory = InventoryManager(nw_device_inventory, spec=nw_device_spec)
    iot_gw = nw_inventory.pop(NwDeviceCategory.HOME, NwDevice.HOME_IOTGW)
    home_router = nw_inventory.pop(NwDeviceCategory.HOME, NwDevice.HOME_ROUTER)
    bs = nw_inventory.pop(NwDeviceCategory.BACKBONE, NwDevice.BASESTATION)
    cloud_switch = nw_inventory.pop(
        NwDeviceCategory.CLOUD, NwDevice.CLOUD_SWITCH)
    # get devices
    device_spec, device_inventory = device_data.create_default_device_data()
    device_inventory = InventoryManager(device_inventory, spec=device_spec)
    nw_device_spec, nw_device_inventory = (
        nw_device_data.create_default_device_data())
    nw_inventory = InventoryManager(nw_device_inventory, spec=nw_device_spec)
    # gen edges
    edge_info = {}
    # SENSROS <-> HOME_IOTGW
    nw_device = iot_gw
    ul_delay = Unit.ms(5)
    dl_delay = Unit.ms(5)
    device = device_inventory.pop(DeviceCategory.SENSOR, Device.THERMAL)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    device = device_inventory.pop(DeviceCategory.SENSOR, Device.THERMAL)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    device = device_inventory.pop(DeviceCategory.SENSOR, Device.CAMERA)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    # PROCESSOR <-> HOME_ROUTER
    nw_device = home_router
    ul_delay = Unit.ms(1)
    dl_delay = Unit.ms(1)
    device = device_inventory.pop(DeviceCategory.PROCESSOR, Device.T2_MICRO)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    device = device_inventory.pop(DeviceCategory.PROCESSOR, Device.T3_LARGE)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    # PROCESSOR <-> CLOUD_SWITCH
    nw_device = cloud_switch
    ul_delay = Unit.ms(1)
    dl_delay = Unit.ms(1)
    device = device_inventory.pop(DeviceCategory.PROCESSOR, Device.T2_MICRO)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    device = device_inventory.pop(DeviceCategory.PROCESSOR, Device.T3_LARGE)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    device = device_inventory.pop(DeviceCategory.PROCESSOR, Device.P3_2XLARGE)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    # ACTUATOR <-> BS
    nw_device = bs
    ul_delay = Unit.ms(20)
    dl_delay = Unit.ms(10)
    device = device_inventory.pop(DeviceCategory.ACTUATOR, Device.PHONE)
    edges = _gen_edge_info(
        device_inventory, device, nw_inventory, nw_device, ul_delay, dl_delay)
    edge_info.update(edges)
    return edge_info


def create_default_network_graph():
    node_info = _create_default_node_info()
    edge_info = _create_default_edge_info()
    graph = topo_graph.create_default_topo_graph()
    graph = graph_utils.gen_graph(node_info, edge_info, base_graph=graph)
    return graph


def export_data():
    node_info = _create_default_node_info()
    edge_info = _create_default_edge_info()
    json_utils.export_bundle(
        'config_default/network_graph.json',
        node_info=node_info,
        edge_info=edge_info)
    _node_info, _edge_info = json_utils.import_bundle(
        common_utils.get_file_path('config_default/network_graph.json'),
        'node_info',
        'edge_info',
    )
    assert _node_info == node_info
    assert _edge_info == edge_info
