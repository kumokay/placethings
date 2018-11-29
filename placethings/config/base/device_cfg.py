from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy

from future.utils import iteritems

from placethings.config.base.utils import string_to_number, SerializableObject


class NetworkInterface(SerializableObject):

    # currently only support these parameters
    _protocol = {'ethernet', 'wifi'}

    def __init__(
            self, protocol='ethernet', n_ports=5, ul_bw='10Mb', dl_bw='10Mb'):
        assert protocol in self._protocol
        assert n_ports > 0
        assert type(ul_bw) == unicode
        assert type(dl_bw) == unicode
        self.protocol = protocol
        self.n_ports = n_ports
        self.ul_bw = string_to_number(ul_bw)
        self.dl_bw = string_to_number(dl_bw)


class ComputationResource(SerializableObject):
    def __init__(
            self, cpu_utilization=0, gpu_utilization=0,
            disk_space='0Mb', ram_size='0Mb'):
        self.cpu_utilization = cpu_utilization
        self.gpu_utilization = gpu_utilization
        self.disk_space = string_to_number(disk_space)
        self.ram_size = string_to_number(ram_size)


class Sensor(SerializableObject):
    _valid_sensor_types = {None, 'camera', 'gps', 'smoke'}
    def __init__(self, sensor_type=None):
        assert type(sensor_type) == unicode
        assert sensor_type in self._valid_sensor_types
        self.sensor_type = sensor_type


class Device(SerializableObject):

    # currently only support these parameters
    _valid_intf_names = {'LAN', 'WAN'}
    _valid_device_types = {
        '_none': 0b0000,
        'network_device': 0b0001,
        'sensor': 0b0010,
        'processor': 0b0100,
        'auctuator': 0b1000,
        '_all': 0b1111}

    def __init__(self, computation_resource=None, interface_dict=None,
            sensor_dict=None, auctuator_dict=None):
        if not computation_resource:
            computation_resource = ComputationResource()
        if not interface_dict:
            interface_dict = {}
        if not sensor_dict:
            sensor_dict = {}
        if not auctuator_dict:
            auctuator_dict = {}
        assert type(computation_resource) == ComputationResource
        assert type(interface_dict) == dict
        assert type(sensor_dict) == dict
        assert type(auctuator_dict) == dict
        self.device_type = device_type
        self.interfaces = {}
        self.computation_resource = computation_resource
        for intf_name, intf in iteritems(interface_dict):
            self.add_interface(intf_name, intf)

    def add_interface(self, name, intf):
        assert type(name) == unicode
        assert type(intf) == NetworkInterface
        assert name in self._valid_intf_names
        assert name not in self.interfaces
        self.interfaces[name] = intf

    def add_computation_resource(self, computation_resource):
        assert type(computation_resource) == ComputationResource
        self.computation_resource = computation_resource


class DeviceSpec(SerializableObject):

    def __init__(self, device_dict=None):
        self.items = {}  # {name: Device}
        if not device_dict:
            device_dict = {}
        for device_name, device_obj in iteritems(device_dict):
            self.add_device(device_name, device_obj)

    def add_device(self, device_name, device_obj):
        assert device_name not in self.items
        self.items[device_name] = device_obj

    def has_device(self, device_name):
        return device_name in self.items

    def get_device(self, device_name):
        return self.items[device_name]


class DeviceInventory(SerializableObject):

    def __init__(self, device_spec, inventory_dict=None):
        assert type(device_spec) == DeviceSpec
        self.device_spec = device_spec
        self.items = {}  # {device_id, device_name}
        if not inventory_dict:
            inventory_dict = {}
        for device_id, device_num in iteritems(inventory_dict):
            self.add_device(device_id, device_num)

    def add_device(self, device_id, device_name):
        assert self.device_spec.has_device(device_name)
        assert device_id not in self.items
        self.items[device_id] = device_name

    def get_device_spec(self, device_id):
        device_name = self.items[device_id]
        return self.device_spec.get_device(device_name)


class NetworkLink(SerializableObject):
    def __init__(self, src_intf_name, dst_intf_name, latency):
        assert latency >= 0
        self.src_intf_name = src_intf_name
        self.dst_intf_name = dst_intf_name
        self.latency = latency


class DeviceData(SerializableObject):
    def __init__(self, nw_device_inventory=None, device_inventory=None):
        if device_inventory:
            assert type(device_inventory) == DeviceInventory
        if nw_device_inventory:
            assert type(nw_device_inventory) == DeviceInventory
        self.device_inventory = device_inventory
        self.nw_device_inventory = nw_device_inventory
        self.device_links = {}
        self.nw_links = {}
        # {src_device: {
        #     dst_device1: link_attr,
        #     dst_device2: link_attr}}

    def _add_single_nw_link(self, src_device_id, dst_device_id, network_link):
        assert type(network_link) == NetworkLink
        src_device = self.nw_device_inventory.get_device_spec(src_device_id)
        dst_device = self.nw_device_inventory.get_device_spec(dst_device_id)
        assert network_link.src_intf_name in src_device.interfaces
        assert network_link.dst_intf_name in dst_device.interfaces
        src_prot = src_device.interfaces[network_link.src_intf_name].protocol
        dst_prot = dst_device.interfaces[network_link.dst_intf_name].protocol
        assert src_prot == dst_prot
        if src_device_id not in self.nw_links:
            self.nw_links[src_device_id] = {}
        assert dst_device_id not in self.nw_links[src_device_id]
        self.nw_links[src_device_id][dst_device_id] = (
            copy.deepcopy(network_link))

    def add_nw_link(self, nw_device1_id, nw_device2_id, network_link):
        self._add_single_nw_link(nw_device1_id, nw_device2_id, network_link)
        network_link2 = copy.deepcopy(network_link)
        network_link2.src_intf_name = network_link.dst_intf_name
        network_link2.dst_intf_name = network_link.src_intf_name
        self._add_single_nw_link(nw_device2_id, nw_device1_id, network_link2)

    def _add_device_to_nwdev_link(self, device_id, nw_device_id, network_link):
        assert type(network_link) == NetworkLink
        src_device = self.device_inventory.get_device_spec(device_id)
        dst_device = self.nw_device_inventory.get_device_spec(nw_device_id)
        assert network_link.src_intf_name in src_device.interfaces
        assert network_link.dst_intf_name in dst_device.interfaces
        src_prot = src_device.interfaces[network_link.src_intf_name].protocol
        dst_prot = dst_device.interfaces[network_link.dst_intf_name].protocol
        assert src_prot == dst_prot
        if device_id not in self.device_links:
            self.device_links[device_id] = {}
        assert nw_device_id not in self.device_links[device_id]
        self.device_links[device_id][nw_device_id] = (
            copy.deepcopy(network_link))

    def _add_nwdev_to_device_link(self, nw_device_id, device_id, network_link):
        assert type(network_link) == NetworkLink
        src_device = self.nw_device_inventory.get_device_spec(nw_device_id)
        dst_device = self.device_inventory.get_device_spec(device_id)
        assert network_link.src_intf_name in src_device.interfaces
        assert network_link.dst_intf_name in dst_device.interfaces
        src_prot = src_device.interfaces[network_link.src_intf_name].protocol
        dst_prot = dst_device.interfaces[network_link.dst_intf_name].protocol
        assert src_prot == dst_prot
        if nw_device_id not in self.device_links:
            self.device_links[nw_device_id] = {}
        assert device_id not in self.device_links[nw_device_id]
        self.device_links[nw_device_id][device_id] = (
            copy.deepcopy(network_link))

    def add_device_link(self, device_id, nw_device_id, network_link):
        self._add_device_to_nwdev_link(device_id, nw_device_id, network_link)
        network_link2 = copy.deepcopy(network_link)
        network_link2.src_intf_name = network_link.dst_intf_name
        network_link2.dst_intf_name = network_link.src_intf_name
        self._add_nwdev_to_device_link(nw_device_id, device_id, network_link2)
