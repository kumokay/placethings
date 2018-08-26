from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import networkx as nx
from matplotlib import pyplot as plt


log = logging.getLogger()


def show_plot(graph):
    nx.draw_networkx(
        graph,
        pos=nx.spring_layout(graph),
        arrows=False,
        with_labels=True,
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

    def rph(cls, n):
        # rate per hour
        return n
