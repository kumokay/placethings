from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from placethings.netgen.netmanager import NetManager
from placethings.definition import GInfo, GnInfo, NwLink, NodeType


log = logging.getLogger()


class NetGen(object):

    _PKT_LOSS = {
        NwLink.WIFI: 0.0,
        NwLink.ETHERNET: 0.0,
    }

    @classmethod
    def create(cls, Gn):
        """
        Create an empty network and add nodes to it.

        Args:
            Gn (nx.DiGraph): topo_device_graph
        Returns:
            net (NetManager)
        """
        net = NetManager.create()
        for node in Gn.nodes():
            node_type = Gn.node[node][GInfo.NODE_TYPE]
            if node_type == NodeType.DEVICE:
                net.addHost(node)
            elif node_type == NodeType.NW_DEVICE:
                net.addSwitch(node)
            else:
                assert False, 'unkown node_type: {}'.format(node_type)
        log.info('*** Creating links')
        for d1, d2 in Gn.edges():
            edge_info = Gn[d1][d2]
            net.addLink(
                d1, d2,
                bw_bps=edge_info[GnInfo.BANDWIDTH],
                delay_ms=edge_info[GnInfo.LATENCY],
                pkt_loss_rate=cls._PKT_LOSS[edge_info[GnInfo.PROTOCOL]])
        return net
