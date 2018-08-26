from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from aenum import Enum, auto


class Const:
    INT_MAX = 2147483647


class Device(Enum):
    T2_MICRO = auto()
    T3_LARGE = auto()
    P3_2XLARGE = auto()


class Flavor(Enum):
    GPU = auto()
    CPU = auto()


class GtInfo(object):
    class GtInfoEnum(Enum):
        TRAFFIC = auto()
        LATENCY_INFO = auto()
        RESOURCE_RQMT = auto()

    class helper(type):
        # used as keys for **kwargs for networkx.Digraph.add_node
        def __getattr__(self, name):
            return getattr(GtInfo.GtInfoEnum, name).name
    __metaclass__ = helper


class GdInfo(object):
    class GdInfoEnum(Enum):
        LATENCY = auto()
        HARDWARE_SPEC = auto()
        COST = auto()
        RESOURCE = auto()
        DEVICE_TYPE = auto()

    class helper(type):
        # used as keys for **kwargs for networkx.Digraph.add_node
        def __getattr__(self, name):
            return getattr(GdInfo.GdInfoEnum, name).name
    __metaclass__ = helper


class GnInfo(object):
    class GnInfoEnum(Enum):
        BANDWIDTH = auto()
        LATENCY = auto()

    class helper(type):
        # used as keys for **kwargs for networkx.Digraph.add_node
        def __getattr__(self, name):
            return getattr(GnInfo.GnInfoEnum, name).name
    __metaclass__ = helper


class Hardware(Enum):
    # shared
    RAM = auto()
    HD = auto()
    CPU = auto()
    GPU = auto()
    GPS = auto()
    # non-shared
    PROXIMITY = auto()
    ACCELEROMETER = auto()
    GYROSCOPE = auto()
    CAMERA = auto()
    # derived data / shared
    NIC_INGRESS = auto()
    NIC_EGRESS = auto()
