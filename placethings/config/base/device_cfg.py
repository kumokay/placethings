from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
import json
import os
import sys

from future.utils import iteritems

from placethings.config.base.utils import size_str_to_bits, time_str_to_ms


class SerializableObject(object):
    def get_classname(self):
        return self.__class__.__name__

    def to_dict(self):
        output = {}
        # put classname here
        output['__classname'] = self.get_classname()
        for objname, obj in iteritems(self.__dict__):
            if isinstance(obj, SerializableObject):
                output[objname] = obj.to_dict()
            else:
                output[objname] = obj
        return output

    def from_dict(self, input_dict):
        for objname, obj in iteritems(input_dict):
            if objname == '__classname':
                assert obj == self.get_classname()
                continue
            if isinstance(obj, dict):
                if '__classname' in obj:
                    classname = obj['__classname']
                    classdef = getattr(sys.modules[__name__], classname, None)
                    if classdef:
                        setattr(self, objname, classdef().from_dict(obj))
                        continue
            setattr(self, objname, obj)
        return self

    def to_json(self):
        return json.dumps(
            self, sort_keys=True, indent=4,
            default=lambda obj: obj.to_dict())

    def from_json(self, json_str):
        output_dict = json.loads(json_str)
        return self.from_dict(output_dict)

    def export_to_file(self, filepath):
        filedir = os.path.dirname(filepath)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        assert os.path.exists(filedir)
        with open(filepath, mode='w') as fp:
            fp.write(self.to_json())
        return os.path.exists(filepath)

    def import_from_file(self, filepath):
        with open(filepath, mode='r') as fp:
            json_str = fp.read()
        return self.from_json(json_str)


class NetworkInterface(SerializableObject):

    # currently only support these parameters
    _protocol = {'ethernet', 'wifi'}

    def __init__(
            self, protocol='undefined', n_ports=0, ul_bw='0Mb', dl_bw='0Mb'):
        assert type(protocol) == unicode
        assert n_ports > 0
        assert type(ul_bw) == unicode
        assert type(dl_bw) == unicode
        assert protocol == 'undefined' or protocol in self._protocol
        ul_bw = size_str_to_bits(ul_bw)
        dl_bw = size_str_to_bits(dl_bw)
        assert ul_bw > 0
        assert dl_bw > 0
        self.protocol = protocol
        self.n_ports = n_ports
        self.ul_bw = ul_bw
        self.dl_bw = dl_bw
        # dynamic attrs
        self.n_available_ports = n_ports


class Network(SerializableObject):
    _valid_network_types = {'on_device', 'on_network_device'}
    _valid_intf_directions = {'egress', 'ingress'}

    def __init__(self, network_type='undefined', interface_dict=None):
        if not interface_dict:
            interface_dict = {}
        assert type(network_type) == unicode
        assert type(interface_dict) == dict
        assert network_type == 'undefined' or (
            network_type in self._valid_network_types)
        for intf_direction, intf_obj in iteritems(interface_dict):
            assert intf_direction in self._valid_intf_directions
        self.network_type = network_type
        self.interface_dict = interface_dict

    def add_interface(self, direction, intf):
        assert type(direction) == unicode
        assert type(intf) == NetworkInterface
        assert direction in self._valid_intf_directions
        assert direction not in self.interface_dict
        self.interface_dict[direction] = intf


class Sensor(SerializableObject):
    # TODO: provide various sensor classes
    _valid_sensor_types = {'camera', 'gps', 'smoke'}

    def __init__(self, sensor_type='undefined'):
        assert type(sensor_type) == unicode
        assert sensor_type == 'undefined' or (
            sensor_type in self._valid_sensor_types)
        self.sensor_type = sensor_type


class Actuator(SerializableObject):
    # TODO: provide various auctuator classes
    _valid_auctuator_types = {'msg_display'}

    def __init__(self, auctuator_type='undefined'):
        assert type(auctuator_type) == unicode
        assert auctuator_type == 'undefined' or (
            auctuator_type in self._valid_auctuator_types)
        self.auctuator_type = auctuator_type


class ComputationResource(SerializableObject):
    def __init__(
            self, cpu_utilization='0%', gpu_utilization='0%',
            disk_space='0Mb', ram_size='0Mb'):
        assert type(cpu_utilization) == unicode
        assert type(gpu_utilization) == unicode
        assert type(disk_space) == unicode
        assert type(ram_size) == unicode
        assert cpu_utilization[-1] == '%'
        assert gpu_utilization[-1] == '%'
        self.cpu_utilization = int(cpu_utilization[:-1])
        self.gpu_utilization = int(gpu_utilization[:-1])
        self.disk_space = size_str_to_bits(disk_space)
        self.ram_size = size_str_to_bits(ram_size)


class ComputationLibrary(SerializableObject):
    def __init__(self, function_dict=None):
        if not function_dict:
            function_dict = {}
        assert type(function_dict) == dict
        self.items = function_dict  # {name, required-resource}

    def add_function(self, name, required_resource):
        assert type(name) == unicode
        assert type(required_resource) == ComputationResource


class Processor(SerializableObject):
    def __init__(self, computation_resource=None, computation_library=None):
        if not computation_resource:
            computation_resource = ComputationResource()
        if not computation_library:
            computation_library = ComputationLibrary()
        assert type(computation_resource) == ComputationResource
        assert type(computation_library) == ComputationLibrary
        self.computation_resource = computation_resource
        self.computation_library = computation_library
        self.available_resource = computation_resource


class Device(SerializableObject):

    def __init__(
            self, processor=None, sensor_dict=None, actuator_dict=None,
            network=None):
        if not processor:
            processor = Processor()
        if not sensor_dict:
            sensor_dict = {}
        if not actuator_dict:
            actuator_dict = {}
        if not network:
            network = Network()
        assert type(processor) == Processor
        assert type(sensor_dict) == dict
        assert type(actuator_dict) == dict
        assert type(network) == Network
        self.processor = processor
        self.sensor_dict = sensor_dict
        self.actuator_dict = actuator_dict
        self.network = network

    def set_processor(self, processor):
        assert type(processor) == Processor
        self.processor = processor

    def set_network(self, network):
        assert type(network) == Network
        self.network = network

    def add_sensor(self, name, sensor):
        assert type(name) == unicode
        assert type(sensor) == Sensor
        assert name not in self.sensor_dict
        self.sensor_dict[name] = sensor

    def add_actuator(self, name, actuator):
        assert type(name) == unicode
        assert type(actuator) == Actuator
        assert name not in self.actuator_dict
        self.actuator_dict[name] = actuator


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


class NetworkLink(SerializableObject):
    def __init__(self, src_intf_name, dst_intf_name, latency):
        assert type(latency) == unicode
        latency = time_str_to_ms(latency)
        self.src_intf_name = src_intf_name
        self.dst_intf_name = dst_intf_name
        self.latency = latency


class DeviceData(SerializableObject):
    def __init__(self, device_spec=None, device_dict=None, link_dict=None):
        if not device_spec:
            device_spec = DeviceSpec()
        if not device_dict:
            device_dict = {}
        if not link_dict:
            link_dict = {}
        assert type(device_spec) == DeviceSpec
        assert type(device_dict) == dict
        assert type(link_dict) == dict
        for device_id, device_name in iteritems(device_dict):
            assert type(device_id) == unicode
            assert type(device_name) == unicode
            assert device_spec.has_device(device_name)
        for src_device_id, dst_device_dict in iteritems(link_dict):
            assert src_device_id in device_dict
            for dst_device_id, network_link in iteritems(dst_device_dict):
                assert dst_device_id in device_dict
                assert type(network_link) == NetworkLink
        self.device_spec = device_spec
        self.device_dict = device_dict  # {device_id, device_obj}
        self.link_dict = link_dict
        # {src_device: {
        #     dst_device1: link_attr,
        #     dst_device2: link_attr}}

    def add_device(self, device_id, device_name):
        assert type(device_id) == unicode
        assert type(device_name) == unicode
        assert self.device_spec.has_device(device_name)
        assert device_id not in self.device_dict
        device_obj = self.device_spec.get_device(device_name)
        self.device_dict[device_id] = copy.deepcopy(device_obj)

    def add_link(self, src_device_id, dst_device_id, network_link):
        assert src_device_id in self.device_dict
        assert dst_device_id in self.device_dict
        assert type(network_link) == NetworkLink
        src_network = self.device_dict[src_device_id].network
        dst_network = self.device_dict[dst_device_id].network
        if src_network.network_type == 'on_device':
            assert dst_network.network_type == 'on_network_device'
        elif src_network.network_type == 'on_network_device':
            assert dst_network.network_type == 'on_device' or (
                dst_network.network_type == 'on_network_device')
        else:
            assert False
        src_intf_name = network_link.src_intf_name
        dst_intf_name = network_link.dst_intf_name
        assert src_intf_name in src_network.interface_dict
        assert dst_intf_name in dst_network.interface_dict
        if src_intf_name == 'egress':
            dst_intf_name == 'ingress'
        elif src_intf_name == 'ingress':
            dst_intf_name = 'egress'
        src_interface = src_network.interface_dict[src_intf_name]
        dst_interface = dst_network.interface_dict[dst_intf_name]
        assert src_interface.protocol == dst_interface.protocol
        assert src_interface.n_available_ports > 0
        assert dst_interface.n_available_ports > 0
        if src_device_id not in self.link_dict:
            self.link_dict[src_device_id] = {}
        assert dst_device_id not in self.link_dict[src_device_id]
        self.link_dict[src_device_id][dst_device_id] = (
            copy.deepcopy(network_link))
        src_interface.n_available_ports -= 1
        dst_interface.n_available_ports -= 1
