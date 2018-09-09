from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import deepcopy
from future.utils import iteritems
import logging

from placethings.config import device_data, nw_device_data, topo_graph
from placethings.config.common import LinkHelper, InventoryManager
from placethings.definition import (
    GdInfo, GnInfo, Hardware, LinkType, LinkInfo, Unit)
from placethings.utils import common_utils, graph_utils, json_utils, plot_utils


log = logging.getLogger()


def _derive_node_info(device_spec, device_inventory):
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


def _get_link_info(device_inventory, nw_inventory, name, link_type):
    if device_inventory.has_device(name):
        spec = device_inventory.get_spec(name)[GdInfo.NIC]
        return (
            spec[LinkInfo.ULINK_BW],
            spec[LinkInfo.DLINK_BW],
            spec[LinkInfo.PROTOCOL])
    elif nw_inventory.has_device(name):
        spec = nw_inventory.get_spec(name)[link_type]
        return (
            spec[LinkInfo.ULINK_BW],
            spec[LinkInfo.DLINK_BW],
            spec[LinkInfo.PROTOCOL])
    else:
        log.error('cannot find {} in inventory'.format(name))
        assert False


def _derive_edge_info(
        device_spec, device_inventory, links,
        nw_device_spec, nw_device_inventory):
    log.info('create default edge (link) info')
    dev_inventory = InventoryManager(device_inventory, spec=device_spec)
    nw_inventory = InventoryManager(nw_device_inventory, spec=nw_device_spec)
    edge_info = {}
    for edge_str, edge_data in iteritems(links):
        n1, n2 = LinkHelper.get_nodes(edge_str)
        link_type = LinkType.LAN
        latency = edge_data[GnInfo.LATENCY]
        ul1, dl1, prot1 = _get_link_info(
            dev_inventory, nw_inventory, n1, link_type)
        ul2, dl2, prot2 = _get_link_info(
            dev_inventory, nw_inventory, n2, link_type)
        assert prot1 == prot2
        edge_info[edge_str] = {
            GnInfo.SRC_LINK_TYPE: link_type,
            GnInfo.DST_LINK_TYPE: link_type,
            GnInfo.BANDWIDTH: min(ul1, dl2),
            GnInfo.LATENCY: latency,
            GnInfo.PROTOCOL: prot1,
        }
    return edge_info


def _derive_graph_info(spec, inventory, links, nw_spec, nw_inventory):
    node_info = _derive_node_info(spec, inventory)
    edge_info = _derive_edge_info(
        spec, inventory, links, nw_spec, nw_inventory)
    return node_info, edge_info


def create_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links,
        is_export=False, graph_filename=None, data_filename=None):
    node_info, edge_info = _derive_graph_info(
        spec, inventory, links, nw_spec, nw_inventory)
    graph = topo_graph.create_topo_graph(nw_spec, nw_inventory, nw_links)
    graph = graph_utils.gen_graph(node_info, edge_info, base_graph=graph)
    if is_export:
        export_graph(graph, graph_filename)
        export_data(node_info, edge_info, data_filename)
    return graph


def create_default_network_graph(
        is_export=False, graph_filename=None, data_filename=None):
    spec, inventory, links = device_data.create_default_device_data()
    nw_spec, nw_inventory, nw_links = (
        nw_device_data.create_default_device_data())
    return create_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links)


def create_graph_from_file(
        device_data_path, nw_data_path,
        is_export=False, graph_filename=None, data_filename=None):
    spec, inventory, links = device_data.import_data(device_data_path)
    nw_spec, nw_inventory, nw_links = nw_device_data.import_data(nw_data_path)
    return create_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links,
        is_export, graph_filename, data_filename)


_DEFAULT_FILE_PATH = 'output/device_graph'


def export_graph(graph, filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH + '.png')
    plot_utils.plot(
        graph,
        with_edge=True,
        which_edge_label=None,
        filepath=filename)


def export_data(node_info, edge_info, filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH + '.json')
    json_utils.export_bundle(
        filename,
        node_info=node_info,
        edge_info=edge_info)
    _node_info, _edge_info = import_data()
    assert _node_info == node_info
    assert _edge_info == edge_info


def import_data(filename=None):
    if not filename:
        filename = common_utils.get_file_path(_DEFAULT_FILE_PATH + '.json')
    node_info, edge_info = json_utils.import_bundle(
        filename,
        'node_info',
        'edge_info',
    )
    return node_info, edge_info
