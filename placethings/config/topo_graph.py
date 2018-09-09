from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config import nw_device_data
from placethings.config.common import LinkHelper, InventoryManager
from placethings.definition import (
    GnInfo, LinkType, LinkInfo, NwDevice, NwDeviceCategory, Unit)
from placethings.utils import common_utils, graph_utils, json_utils


log = logging.getLogger()


def _create_default_node_info():
    """
    Returns:
        node_info (dict): {node_name (str): node_data (dict)}, where
            node_data = { data_name (GtInfo): data (any) }
    """
    log.info('create default node (nw device) info')
    device_spec, device_inventory = nw_device_data.create_default_device_data()
    node_info = nw_device_data.derive_device_info(
        device_spec, device_inventory)
    return node_info


def _get_link_info(inventory, name, link_type):
    spec = inventory.get_spec(name)[link_type]
    return (
        spec[LinkInfo.ULINK_BW],
        spec[LinkInfo.DLINK_BW],
        spec[LinkInfo.PROTOCOL])


def _gen_edge_info(
        inventory, n1, link_type1, n2, link_type2, ul_delay, dl_delay):
    ul1, dl1, prot1 = _get_link_info(inventory, n1, link_type1)
    ul2, dl2, prot2 = _get_link_info(inventory, n2, link_type2)
    assert prot1 == prot2
    prot = prot1
    edge_info = {}
    edge_info[LinkHelper.get_edge(n1, n2)] = {
        GnInfo.SRC_LINK_TYPE: link_type1,
        GnInfo.DST_LINK_TYPE: link_type2,
        GnInfo.BANDWIDTH: min(ul1, dl2),
        GnInfo.LATENCY: ul_delay,
        GnInfo.PROTOCOL: prot,
    }
    edge_info[LinkHelper.get_edge(n2, n1)] = {
        GnInfo.SRC_LINK_TYPE: link_type2,
        GnInfo.DST_LINK_TYPE: link_type1,
        GnInfo.BANDWIDTH: min(ul2, dl1),
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
    device_spec, device_inventory = nw_device_data.create_default_device_data()
    inventory = InventoryManager(device_inventory, spec=device_spec)
    # get devices
    iot_gw = inventory.pop(NwDeviceCategory.HOME, NwDevice.HOME_IOTGW)
    home_router = inventory.pop(NwDeviceCategory.HOME, NwDevice.HOME_ROUTER)
    bb_switch = inventory.pop(NwDeviceCategory.BACKBONE, NwDevice.BB_SWITCH)
    bs = inventory.pop(NwDeviceCategory.BACKBONE, NwDevice.BASESTATION)
    cloud_switch = inventory.pop(NwDeviceCategory.CLOUD, NwDevice.CLOUD_SWITCH)
    # gen edges
    edge_info = {}
    # HOME_IOTGW <-> HOME_SWTICH
    ul_delay = Unit.ms(1)
    dl_delay = Unit.ms(1)
    edges = _gen_edge_info(
        inventory, iot_gw, LinkType.WAN, home_router, LinkType.LAN,
        ul_delay, dl_delay)
    edge_info.update(edges)
    # HOME_SWTICH <-> BB_SWTICH
    ul_delay = Unit.ms(10)
    dl_delay = Unit.ms(10)
    edges = _gen_edge_info(
        inventory, home_router, LinkType.WAN, bb_switch, LinkType.ANY,
        ul_delay, dl_delay)
    edge_info.update(edges)
    # BASESTATION <-> BB_SWTICH
    ul_delay = Unit.ms(10)
    dl_delay = Unit.ms(10)
    edges = _gen_edge_info(
        inventory, bs, LinkType.WAN, bb_switch, LinkType.ANY,
        ul_delay, dl_delay)
    edge_info.update(edges)
    # CLOUD_SWTICH <-> BB_SWTICH
    ul_delay = Unit.ms(20)
    dl_delay = Unit.ms(20)
    edges = _gen_edge_info(
        inventory, cloud_switch, LinkType.WAN, bb_switch, LinkType.ANY,
        ul_delay, dl_delay)
    edge_info.update(edges)
    return edge_info


def create_default_topo_graph():
    node_info = _create_default_node_info()
    edge_info = _create_default_edge_info()
    graph = graph_utils.gen_graph(node_info, edge_info)
    return graph


def export_data():
    node_info = _create_default_node_info()
    edge_info = _create_default_edge_info()
    json_utils.export_bundle(
        'config_default/topo_graph.json',
        node_info=node_info,
        edge_info=edge_info)
    _node_info, _edge_info = import_data()
    assert _node_info == node_info
    assert _edge_info == edge_info


def import_data():
    node_info, edge_info = json_utils.import_bundle(
        common_utils.get_file_path('config_default/topo_graph.json'),
        'node_info',
        'edge_info',
    )
    return node_info, edge_info
