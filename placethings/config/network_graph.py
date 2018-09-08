from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config import device_data
from placethings.config.common import LinkHelper, InventoryManager
from placethings.definition import (
    GnInfo, LinkType, LinkInfo, NwDevice, NwDeviceCategory)
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
    spec = inventory.get_spec(name)
    return (
        spec[LinkInfo.ULINK_BW],
        spec[LinkInfo.DLINK_BW],
        spec[LinkInfo.PROTOCOL])


def _gen_edge_info(nw_inventory, nw_device, device_inventory, device):
    ul1, dl1, prot1 = _get_link_info(nw_inventory, nw_device, link_type1)
    ul2, dl2, prot2 = _get_link_info(inventory2, n2, link_type2)
    assert prot1 == prot2
    prot = prot1
    edge_info = {}
    edge_info[LinkHelper.get_edge(n1, n2)] = {
        GnInfo.SRC_LINK_TYPE: link_type1,
        GnInfo.DST_LINK_TYPE: link_type2,
        GnInfo.BANDWIDTH: min(ul1, dl2),
        GnInfo.PROTOCOL: prot,
    }
    edge_info[LinkHelper.get_edge(n2, n1)] = {
        GnInfo.SRC_LINK_TYPE: link_type2,
        GnInfo.DST_LINK_TYPE: link_type1,
        GnInfo.BANDWIDTH: min(ul2, dl1),
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
    device_spec, device_inventory = device_data.create_default_device_data()
    inventory = InventoryManager(device_inventory, spec=device_spec)
    # gen edges
    edge_info = {}
    # HOME_IOTGW <-> HOME_SWTICH
    edges = _gen_edge_info(
        inventory, n1, LinkType.WAN, n2, LinkType.LAN)
    edge_info.update(edges)
