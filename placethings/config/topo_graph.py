from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy
from future.utils import iteritems
import logging

from placethings.config import nw_device_data
from placethings.config.common import LinkHelper, InventoryManager
from placethings.definition import GnInfo, LinkInfo
from placethings.utils import common_utils, graph_utils, json_utils


log = logging.getLogger()


def _derive_node_info(device_spec, device_inventory):
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


def _get_link_info(inventory, name, link_type):
    spec = inventory.get_spec(name)[link_type]
    return (
        spec[LinkInfo.ULINK_BW],
        spec[LinkInfo.DLINK_BW],
        spec[LinkInfo.PROTOCOL])


def _derive_edge_info(nw_device_spec, nw_device_inventory, links):
    inventory = InventoryManager(nw_device_inventory, spec=nw_device_spec)
    edge_info = {}
    for edge_str, edge_data in iteritems(links):
        n1, n2 = LinkHelper.get_nodes(edge_str)
        link_type1 = edge_data[GnInfo.SRC_LINK_TYPE]
        link_type2 = edge_data[GnInfo.DST_LINK_TYPE]
        latency = edge_data[GnInfo.LATENCY]
        ul1, dl1, prot1 = _get_link_info(inventory, n1, link_type1)
        ul2, dl2, prot2 = _get_link_info(inventory, n2, link_type2)
        assert prot1 == prot2
        edge_info[edge_str] = {
            GnInfo.SRC_LINK_TYPE: link_type1,
            GnInfo.DST_LINK_TYPE: link_type2,
            GnInfo.BANDWIDTH: min(ul1, dl2),
            GnInfo.LATENCY: latency,
            GnInfo.PROTOCOL: prot1,
        }
    return edge_info


def _derive_graph_info(spec, inventory, links):
    node_info = _derive_node_info(spec, inventory)
    edge_info = _derive_edge_info(spec, inventory, links)
    return node_info, edge_info


def create_topo_graph(spec, inventory, links):
    node_info, edge_info = _derive_graph_info(spec, inventory, links)
    graph = graph_utils.gen_graph(node_info, edge_info)
    return graph


def create_default_topo_graph():
    spec, inventory, links = nw_device_data.create_default_device_data()
    return create_topo_graph(spec, inventory, links)


def create_topo_graph_from_file(filepath):
    spec, inventory, links = nw_device_data.import_data(filepath)
    return create_topo_graph(spec, inventory, links)


_DEFAULT_FILE_PATH = 'output/topo_graph.json'


def export_data(filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH)
    spec, inventory, links = nw_device_data.create_default_device_data()
    node_info, edge_info = _derive_graph_info(spec, inventory, links)
    json_utils.export_bundle(
        filename,
        node_info=node_info,
        edge_info=edge_info)
    _node_info, _edge_info = import_data()
    assert _node_info == node_info
    assert _edge_info == edge_info


def import_data(filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH)
    node_info, edge_info = json_utils.import_bundle(
        filename,
        'node_info',
        'edge_info',
    )
    return node_info, edge_info
