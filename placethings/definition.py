from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from aenum import Enum, auto


INT_MAX = 2147483647


class Device(Enum):
    T3_MICRO = auto()
    T3_LARGE = auto()
    P3_2XLARGE = auto()


class Flavor(Enum):
    GPU = auto()
    CPU = auto()


class GtInfo(type):
    # used as keys for **kwargs for networkx.Digraph.add_node
    DATA_SZ = 'DATA_SZ'
    DATA_IN = 'DATA_IN'
    DATA_OUT = 'DATA_OUT'
    LATENCY_INFO = 'LATENCY_INFO'
    RESOURCE_RQMT = 'RESOURCE_RQMT'
    SENSOR_RQMT = 'SENSOR_RQMT'


class Resource(Enum):
    RAM = auto()
    HD = auto()
    GPU = auto()
    CPU = auto()


class Sensor(Enum):
    GPS = auto()
    CAMERA = auto()


class Unit(object):

    _UNIT = 1

    @classmethod
    def ms(cls, n):
        return n * cls._UNIT

    @classmethod
    def sec(cls, n):
        return n * cls.ms(1000)

    @classmethod
    def byte(cls, n):
        return n * cls._UNIT

    @classmethod
    def kb(cls, n):
        return n * cls.byte(1024)

    @classmethod
    def mb(cls, n):
        return n * cls.kb(1024)

    @classmethod
    def gb(cls, n):
        return n * cls.mb(1024)

    @classmethod
    def tb(cls, n):
        return n * cls.gb(1024)
