from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import networkx as nx
from matplotlib import pyplot as plt


log = logging.getLogger()


def show_plot(graph, with_edge=True, which_edge_label=None):
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(
        graph,
        pos=pos,
        nodelist=None,
        node_size=300,
        node_color='r',
        node_shape='o',
    )
    nx.draw_networkx_labels(
        graph,
        pos=pos,
        labels=None,
        font_size=12,
        font_color='k',
        font_family='sans-serif',
        font_weight='normal',
    )
    if with_edge:
        nx.draw_networkx_edges(
            graph,
            pos=pos,
            edgelist=None,
            width=1.0,
            edge_color='k',
            style='solid',
        )
        if not which_edge_label:
            edge_labels = {}
        else:
            edge_labels = {
                (src, dst): attr[which_edge_label]
                for src, dst, attr in graph.edges(data=True)
            }
        nx.draw_networkx_edge_labels(
            graph,
            pos=pos,
            edge_labels=edge_labels,
            label_pos=0.5,
            font_size=10,
            font_color='k',
            font_family='sans-serif',
            font_weight='normal',
        )
    plt.show(graph)


class Unit(object):

    _UNIT = 1

    @classmethod
    def percentage(cls, n):
        return n * cls._UNIT

    @classmethod
    def ms(cls, n):
        return n * cls._UNIT

    @classmethod
    def sec(cls, n):
        return n * cls.ms(1000)

    @classmethod
    def bit(cls, n):
        return n * cls._UNIT

    @classmethod
    def byte(cls, n):
        return n * cls.bit(8)

    @classmethod
    def kbyte(cls, n):
        return n * cls.byte(1024)

    @classmethod
    def mbyte(cls, n):
        return n * cls.kbyte(1024)

    @classmethod
    def gbyte(cls, n):
        return n * cls.mbyte(1024)

    @classmethod
    def tbyte(cls, n):
        return n * cls.gbyte(1024)

    @classmethod
    def bps(cls, n):
        return n * cls._UNIT

    @classmethod
    def kbps(cls, n):
        return n * cls.bps(1024)

    @classmethod
    def mbps(cls, n):
        return n * cls.kbps(1024)

    @classmethod
    def gbps(cls, n):
        return n * cls.mbps(1024)

    @classmethod
    def tbps(cls, n):
        return n * cls.gbps(1024)

    @classmethod
    def rph(cls, n):
        # rate per hour
        return n
