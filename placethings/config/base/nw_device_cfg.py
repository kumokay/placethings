from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
import json
import os

from future.utils import iteritems


"""
"NwDevice.FIELD_SWITCH": {
    "LinkType.WAN": {
        "LinkInfo.ULINK_BW": 2147483647,
        "LinkInfo.PROTOCOL": "NwLink.ETHERNET",
        "LinkInfo.N_LINKS": 1,
        "LinkInfo.DLINK_BW": 2147483647
    },
    "LinkType.LAN": {
        "LinkInfo.ULINK_BW": 419430400,
        "LinkInfo.PROTOCOL": "NwLink.ETHERNET",
        "LinkInfo.N_LINKS": 2147483647,
        "LinkInfo.DLINK_BW": 419430400
    }
}
"""


def string_to_number(byte_repr_str):
    """
    Args:
        byte_repr_str (str): e.g. 100MB, 10Kb; float is not allowed
    Returns:
        num (int): bytes
    """
    is_parsing_unit = False
    num = 0
    for ch in byte_repr_str:
        if ch.isdigit():
            assert is_parsing_unit is False
            num = num * 10 + int(ch)
            continue
        else:
            is_parsing_unit = True

        if ch.lower() == 'k':
            num = num * 1024
        elif ch.lower() == 'm':
            num = num * 1024 * 1024
        elif ch.lower() == 'g':
            num = num * 1024 * 1024 * 1024
        elif ch == 'B':
            num = num * 8
        elif ch == 'b':
            num = num * 1
        else:
            # invalid format
            assert(False)
    return num


class SerializableObject(object):
    def to_dict(self):
        ret = {}
        for objname, obj in iteritems(self.__dict__):
            if isinstance(obj, SerializableObject):
                ret[objname] = obj.to_dict()
            else:
                ret[objname] = obj
        return ret

    def to_json(self):
        return json.dumps(
            self, sort_keys=True, indent=4,
            default=lambda obj: obj.to_dict())

    def export_to_file(self, filepath):
        filedir = os.path.dirname(filepath)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        assert os.path.exists(filedir)
        with open(filepath, mode='w') as fp:
            fp.write(self.to_json())
        return os.path.exists(filepath)


class NetworkInterface(SerializableObject):

    # currently only support these parameters
    _protocol = {'ethernet', 'wifi'}

    def __init__(
            self, protocol='ethernet', n_ports=5, ul_bw='10Mb', dl_bw='10Mb'):
        assert protocol in self._protocol
        self.protocol = protocol
        assert n_ports > 0
        self.n_ports = n_ports
        assert type(ul_bw) == unicode
        self.ul_bw = string_to_number(ul_bw)
        assert type(dl_bw) == unicode
        self.dl_bw = string_to_number(dl_bw)


class NetworkDevice(SerializableObject):

    # currently only support these parameters
    _intf_name = {'LAN', 'WAN'}

    def __init__(self, name, interface_dict=None):
        assert type(name) == unicode
        self.name = name
        self.interfaces = {}
        if not interface_dict:
            interface_dict = {}
        for intf_name, intf in iteritems(interface_dict):
            self.add_interface(intf_name, intf)

    def add_interface(self, name, intf):
        assert type(name) == unicode
        assert type(intf) == NetworkInterface
        assert name in self._intf_name
        assert name not in self.interfaces
        self.interfaces[name] = intf


class NetworkDeviceSpec(SerializableObject):

    def __init__(self, nw_device_list=None):
        # {name: NetworkDevice}
        self.items = {}
        if not nw_device_list:
            nw_device_list = []
        for nw_device in nw_device_list:
            self.add_nw_device(nw_device)

    def add_nw_device(self, nw_device):
        assert nw_device.name not in self.items
        self.items[nw_device.name] = nw_device

    def has_nw_device(self, nw_device):
        return nw_device in self.items

    def get_nw_device(self, nw_device_name):
        return self.items[nw_device_name]


class NetworkDeviceInventory(SerializableObject):

    def __init__(self, nw_device_spec, nw_inventory_dict=None):
        assert type(nw_device_spec) == NetworkDeviceSpec
        self.nw_device_spec = nw_device_spec
        self.items = {}  # {nw_device_id, nw_device_name}
        if not nw_inventory_dict:
            nw_inventory_dict = {}
        for nw_device_name, nw_device_num in iteritems(nw_inventory_dict):
            self.set_nw_device_number(nw_device_name, nw_device_num)

    def add_device(self, nw_device_id, nw_device_name):
        assert self.nw_device_spec.has_nw_device(nw_device_name)
        assert nw_device_id not in self.items
        self.items[nw_device_id] = nw_device_name

    def get_nw_device_spec(self, nw_device_id):
        nw_device_name = self.items[nw_device_id]
        return self.nw_device_spec.get_nw_device(nw_device_name)


class NetworkLink(SerializableObject):
    def __init__(self, src_intf_name, dst_intf_name, latency):
        assert src_intf_name in NetworkDevice._intf_name
        assert dst_intf_name in NetworkDevice._intf_name
        assert latency >= 0
        self.src_intf_name = src_intf_name
        self.dst_intf_name = dst_intf_name
        self.latency = latency


class NetworkDeviceData(SerializableObject):
    def __init__(self, nw_device_inventory):
        assert type(nw_device_inventory) == NetworkDeviceInventory
        self.nw_device_inventory = nw_device_inventory
        self.nw_device_links = {}
        # {src_device: {
        #     dst_device1: link_attr,
        #     dst_device2: link_attr}}

    def add_link(self, src_device_id, dst_device_id, network_link):
        assert type(network_link) == NetworkLink
        src_device = self.nw_device_inventory.get_nw_device_spec(src_device_id)
        dst_device = self.nw_device_inventory.get_nw_device_spec(dst_device_id)
        assert network_link.src_intf_name in src_device.interfaces
        assert network_link.dst_intf_name in dst_device.interfaces
        if src_device_id not in self.nw_device_links:
            self.nw_device_links[src_device_id] = {}
        assert dst_device_id not in self.nw_device_links[src_device_id]
        self.nw_device_links[src_device_id][dst_device_id] = (
            copy.deepcopy(network_link))
