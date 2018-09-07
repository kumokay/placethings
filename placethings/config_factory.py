from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import range
from copy import deepcopy
from future.utils import iteritems
import logging

from placethings.definition import (
    Const, Device, DeviceCategory, Flavor, GtInfo, GdInfo, GnInfo,
    Hardware, NetworkDevice, NetworkLink, Unit)
from placethings.utils import json_utils, common_utils


log = logging.getLogger()

_LINK_SYMBOL = ' -> '


class InventoryManager(object):
    @staticmethod
    def _gen_device_name(device_type, device_id):
        return '{}.{}'.format(device_type.name, device_id)

    def _n_device(self, device_cat, device_type):
        return self.inventory[device_cat][device_type]

    def reset_inventory_record(self):
        record = {}
        for device_cat in self.inventory:
            record[device_cat] = {}
            for device_type in self.inventory[device_cat]:
                n_device = self._n_device(device_cat, device_type)
                device_list = []
                for device_id in range(n_device):
                    device_list.append(
                        self._gen_device_name(device_type, device_id))
                record[device_cat][device_type] = device_list
        return record

    def __init__(self, inventory):
        self.inventory = inventory
        self.record = self.reset_inventory_record()

    def pop(self, device_cat, device_type):
        device_list = self.record[device_cat][device_type]
        assert len(device_list) > 0
        return device_list.pop(0)  # pop the first item

    def push(self, device_name, device_cat, device_type):
        device_list = self.record[device_cat][device_type]
        assert len(device_list) < self._n_device(device_cat, device_type)
        device_list.append(device_name)

    def export_to_set(self):
        all_devices = set()
        n_total = 0
        for device_cat in self.inventory:
            self.record[device_cat] = {}
            for device_type in self.inventory[device_cat]:
                n_device = self._n_device(device_cat, device_type)
                for device_id in range(n_device):
                    all_devices.add(
                        self._gen_device_name(device_type, device_id))
                n_total += n_device
        assert len(all_devices) == n_total
        return all_devices


class SetManager(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def get(self, data):
        assert data in self.dataset, '{} not in {}'.format(data, self.dataset)
        return data

    def export_to_list(self):
        return list(self.dataset)


def gen_link_str(src, dst):
    return '{}{}{}'.format(src, _LINK_SYMBOL, dst)


def get_src_dst(link_str):
    src, dst = link_str.split(_LINK_SYMBOL)
    return src, dst


def _create_default_task_info():
    log.info('create default task info')
    tasks = SetManager(
        {
            'task_thermal_loc1',
            'task_thermal_loc2',
            'task_camera',
            'task_broadcast',
            'task_getAvgTemperature',
            'task_findObject',
            'task_checkAbnormalEvent',
            'task_sentNotificatoin',
        }
    )
    task_info = {
        tasks.get('task_thermal_loc1'): {
            GtInfo.LATENCY_INFO: {},
            GtInfo.RESRC_RQMT: {}
        },
        tasks.get('task_thermal_loc2'): {
            GtInfo.LATENCY_INFO: {},
            GtInfo.RESRC_RQMT: {},
        },
        tasks.get('task_camera'): {
            GtInfo.LATENCY_INFO: {},
            GtInfo.RESRC_RQMT: {},
        },
        tasks.get('task_broadcast'): {
            GtInfo.LATENCY_INFO: {},
            GtInfo.RESRC_RQMT: {},
        },
        tasks.get('task_getAvgTemperature'): {
            GtInfo.LATENCY_INFO: {
                Device.T2_MICRO: {
                    # TODO: assume one flavor per device type for now.
                    # may extend to multiple flavor later
                    Flavor.CPU: Unit.ms(15),
                },
                Device.T3_LARGE: {
                    Flavor.CPU: Unit.ms(10),
                },
                Device.P3_2XLARGE: {
                    Flavor.CPU: Unit.ms(5),
                },
            },
            GtInfo.RESRC_RQMT: {
                Flavor.CPU: {
                    Hardware.RAM: Unit.mbyte(1),
                    Hardware.HD: Unit.kbyte(3),
                    Hardware.GPU: Unit.percentage(0),
                    Hardware.CPU: Unit.percentage(5),
                }
            },
        },
        tasks.get('task_findObject'): {
            GtInfo.LATENCY_INFO: {
                Device.T2_MICRO: {
                    Flavor.CPU: Unit.sec(6),
                },
                Device.T3_LARGE: {
                    Flavor.CPU: Unit.sec(2),
                },
                Device.P3_2XLARGE: {
                    Flavor.GPU: Unit.ms(600),
                },
            },
            GtInfo.RESRC_RQMT: {
                Flavor.GPU: {
                    Hardware.RAM: Unit.gbyte(4),
                    Hardware.HD: Unit.mbyte(500),
                    Hardware.GPU: Unit.percentage(60),
                    Hardware.CPU: Unit.percentage(5),
                },
                Flavor.CPU: {
                    Hardware.RAM: Unit.gbyte(1),
                    Hardware.HD: Unit.mbyte(300),
                    Hardware.GPU: Unit.percentage(0),
                    Hardware.CPU: Unit.percentage(80),
                },
            },
        },
        tasks.get('task_checkAbnormalEvent'): {
            GtInfo.LATENCY_INFO: {
                Device.T2_MICRO: {
                    Flavor.CPU: Unit.ms(5),
                },
                Device.T3_LARGE: {
                    Flavor.CPU: Unit.ms(5),
                },
                Device.P3_2XLARGE: {
                    Flavor.CPU: Unit.ms(5),
                },
            },
            GtInfo.RESRC_RQMT: {
                Flavor.CPU: {
                    Hardware.RAM: Unit.mbyte(1),
                    Hardware.HD: Unit.kbyte(3),
                    Hardware.GPU: Unit.percentage(0),
                    Hardware.CPU: Unit.percentage(5),
                },
            },
        },
        tasks.get('task_sentNotificatoin'): {
            GtInfo.LATENCY_INFO: {
                Device.T2_MICRO: {
                    Flavor.CPU: Unit.ms(5),
                },
                Device.T3_LARGE: {
                    Flavor.CPU: Unit.ms(5),
                },
                Device.P3_2XLARGE: {
                    Flavor.CPU: Unit.ms(5),
                },
            },
            GtInfo.RESRC_RQMT: {
                Flavor.CPU: {
                    Hardware.RAM: Unit.mbyte(1),
                    Hardware.HD: Unit.kbyte(3),
                    Hardware.GPU: Unit.percentage(0),
                    Hardware.CPU: Unit.percentage(5),
                },
            },
        },
    }

    edge_info = {}
    t1 = tasks.get('task_thermal_loc1')
    t2 = tasks.get('task_getAvgTemperature')
    edge_info[gen_link_str(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.kbyte(1),
    }
    t1 = tasks.get('task_thermal_loc2')
    t2 = tasks.get('task_getAvgTemperature')
    edge_info[gen_link_str(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.kbyte(1),
    }
    t1 = tasks.get('task_getAvgTemperature')
    t2 = tasks.get('task_checkAbnormalEvent')
    edge_info[gen_link_str(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.byte(1),
    }
    t1 = tasks.get('task_camera')
    t2 = tasks.get('task_findObject')
    edge_info[gen_link_str(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.mbyte(10),
    }
    t1 = tasks.get('task_findObject')
    t2 = tasks.get('task_checkAbnormalEvent')
    edge_info[gen_link_str(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.byte(10),
    }
    t1 = tasks.get('task_checkAbnormalEvent')
    t2 = tasks.get('task_sentNotificatoin')
    edge_info[gen_link_str(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.byte(1),
    }
    t1 = tasks.get('task_sentNotificatoin')
    t2 = tasks.get('task_broadcast')
    edge_info[gen_link_str(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.byte(1),
    }
    return task_info, edge_info


def _init_mapping(task_set, device_set):
    tasks = SetManager(task_set)
    devices = SetManager(device_set)
    src_map = {}
    src_map[tasks.get('task_thermal_loc1')] = devices.get('THERMAL.0')
    src_map[tasks.get('task_thermal_loc2')] = devices.get('THERMAL.1')
    src_map[tasks.get('task_camera')] = devices.get('CAMERA.0')
    dst_map = {}
    dst_map[tasks.get('task_broadcast')] = devices.get('PHONE.0')
    return src_map, dst_map


def create_default_task_graph():
    task_info, edge_info = _create_default_task_info()
    task_set = set(task_info)
    device_set = InventoryManager(create_default_inventory()).export_to_set()
    src_map, dst_map = _init_mapping(task_set, device_set)
    return task_info, edge_info, src_map, dst_map


def create_default_inventory():
    log.info('create default device inventory')
    device_inventory = {
        DeviceCategory.ACTUATOR: {
            Device.PHONE: 1,
        },
        DeviceCategory.PROCESSOR: {
            Device.T2_MICRO: 20,
            Device.T3_LARGE: 10,
            Device.P3_2XLARGE: 1,
        },
        DeviceCategory.SENSOR: {
            Device.THERMAL: 2,
            Device.CAMERA: 1,
        },
    }
    return device_inventory


def _create_default_device_spec():
    device_spec = {
        DeviceCategory.ACTUATOR: {
            Device.PHONE: {
                GdInfo.COST: Unit.rph(0),
                GdInfo.HARDWARE: {},
            },
        },
        DeviceCategory.PROCESSOR: {
            Device.T2_MICRO: {
                GdInfo.COST: Unit.rph(0.0116),
                GdInfo.HARDWARE: {
                    Hardware.RAM: Unit.gbyte(1),
                    Hardware.HD: Unit.gbyte(30),
                    Hardware.CPU: 1,
                    Hardware.GPU: 0,
                    Hardware.NIC_INGRESS: Unit.mbps(100),
                    Hardware.NIC_EGRESS: Unit.mbps(100),
                },
            },
            Device.T3_LARGE: {
                GdInfo.COST: Unit.rph(0.0928),
                GdInfo.HARDWARE: {
                    Hardware.RAM: Unit.gbyte(8),
                    Hardware.HD: Unit.tbyte(16),
                    Hardware.CPU: 2,
                    Hardware.GPU: 0,
                    Hardware.NIC_INGRESS: Unit.gbps(1),
                    Hardware.NIC_EGRESS: Unit.gbps(1),
                },
            },
            Device.P3_2XLARGE: {
                GdInfo.COST: Unit.rph(3.06),
                GdInfo.HARDWARE: {
                    Hardware.RAM: Unit.gbyte(16),
                    Hardware.HD: Unit.tbyte(16),
                    Hardware.CPU: 8,
                    Hardware.GPU: 1,
                    Hardware.NIC_INGRESS: Unit.gbps(10),
                    Hardware.NIC_EGRESS: Unit.gbps(10),
                },
            },
        },
        DeviceCategory.SENSOR: {
            Device.THERMAL: {
                GdInfo.COST: Unit.rph(0),
                GdInfo.HARDWARE: {},
            },
            Device.CAMERA: {
                GdInfo.COST: Unit.rph(0),
                GdInfo.HARDWARE: {},
            },
        },
    }
    return device_spec


def create_default_device_data():
    device_spec = _create_default_device_spec()
    device_inventory = create_default_inventory()
    return device_spec, device_inventory


def derive_device_info(cls, device_spec, device_inventory):
    all_device_info = {}
    inventory_manager = InventoryManager(device_inventory)
    for device_cat, inventory_info in iteritems(inventory_manager.record):
        for device_type, device_list in iteritems(inventory_info):
            for device_name in device_list:
                # copy hardware spec
                spec = device_spec[device_cat][device_type]
                device_info = {
                    GdInfo.DEVICE_CAT: device_cat,
                    GdInfo.DEVICE_TYPE: device_type,
                    GdInfo.COST: spec[GdInfo.COST],
                    GdInfo.HARDWARE: spec[GdInfo.HARDWARE],
                    GdInfo.RESRC: deepcopy(spec[GdInfo.HARDWARE]),
                }
                # special setting for RESRC info of GPU/CPU
                for hw_type in [Hardware.CPU, Hardware.GPU]:
                    if hw_type in device_info[GdInfo.RESRC]:
                        device_info[GdInfo.RESRC][hw_type] = (
                            Unit.percentage(100))
                all_device_info[device_name] = device_info
    return all_device_info


def _create_default_network_devices():
    log.info('create default network devices')
    devices = SetManager(
        {'HomeIotGW', 'HomeRouter', 'ISPSwitch', 'BaseStation', 'CloudSwitch'}
    )
    device_spec = {
        devices.get('HomeIotGW'): {
            GnInfo.DEVICE_TYPE: NetworkDevice.AP,
            GnInfo.AVAILABLE_LINKS: 20,
            GnInfo.ULINK_BW: Unit.mbps(60),
            GnInfo.DLINK_BW: Unit.mbps(60),
            GnInfo.LINK_TYPE: NetworkLink.WLAN,
        },
        devices.get('HomeRouter'): {
            GnInfo.DEVICE_TYPE: NetworkDevice.SWITCH,
            GnInfo.AVAILABLE_LINKS: 8,
            GnInfo.ULINK_BW: Unit.mbps(100),
            GnInfo.DLINK_BW: Unit.mbps(100),
            GnInfo.LINK_TYPE: NetworkLink.LAN,
        },
        devices.get('BaseStation'): {
            GnInfo.DEVICE_TYPE: NetworkDevice.BS,
            GnInfo.AVAILABLE_LINKS: Const.INT_MAX,
            GnInfo.ULINK_BW: Unit.mbps(60),
            GnInfo.DLINK_BW: Unit.mbps(150),
            GnInfo.LINK_TYPE: NetworkLink.LTE,
        },
        devices.get('ISPSwitch'): {
            GnInfo.DEVICE_TYPE: NetworkDevice.SWITCH,
            GnInfo.AVAILABLE_LINKS: Const.INT_MAX,
            GnInfo.ULINK_BW: Unit.mbps(800),
            GnInfo.DLINK_BW: Unit.mbps(800),
            GnInfo.LINK_TYPE: NetworkLink.BACKBONE,
        },
        devices.get('CloudSwitch'): {
            GnInfo.DEVICE_TYPE: NetworkDevice.SWITCH,
            GnInfo.AVAILABLE_LINKS: Const.INT_MAX,
            GnInfo.ULINK_BW: Unit.mbps(400),
            GnInfo.DLINK_BW: Unit.mbps(400),
            GnInfo.LINK_TYPE: NetworkLink.BACKBONE,
        }
    }
    return device_spec


def _create_default_network_links(nw_devices):
    nw_devices = SetManager(nw_devices)
    links = {}
    d1 = nw_devices.get('HomeIotGW')
    d2 = nw_devices.get('HomeRouter')
    links[gen_link_str(d1, d2)] = {
        GnInfo.LATENCY: Unit.ms(1),
        GnInfo.BANDWIDTH: Unit.mbps(100),
    }
    links[gen_link_str(d2, d1)] = {
        GnInfo.LATENCY: Unit.ms(1),
        GnInfo.BANDWIDTH: Unit.mbps(100),
    }
    d1 = nw_devices.get('HomeRouter')
    d2 = nw_devices.get('ISPSwitch')
    links[gen_link_str(d1, d2)] = {
        GnInfo.LATENCY: Unit.ms(5),
        GnInfo.BANDWIDTH: Unit.mbps(100),
    }
    links[gen_link_str(d2, d1)] = {
        GnInfo.LATENCY: Unit.ms(5),
        GnInfo.BANDWIDTH: Unit.mbps(100),
    }
    d1 = nw_devices.get('BaseStation')
    d2 = nw_devices.get('ISPSwitch')
    links[gen_link_str(d1, d2)] = {
        GnInfo.LATENCY: Unit.ms(5),
        GnInfo.BANDWIDTH: Const.INT_MAX,
    }
    links[gen_link_str(d2, d1)] = {
        GnInfo.LATENCY: Unit.ms(5),
        GnInfo.BANDWIDTH: Const.INT_MAX,
    }
    d1 = nw_devices.get('CloudSwitch')
    d2 = nw_devices.get('ISPSwitch')
    links[gen_link_str(d1, d2)] = {
        GnInfo.LATENCY: Unit.ms(5),
        GnInfo.BANDWIDTH: Const.INT_MAX,
    }
    links[gen_link_str(d2, d1)] = {
        GnInfo.LATENCY: Unit.ms(5),
        GnInfo.BANDWIDTH: Const.INT_MAX,
    }
    return links


def _create_default_deployment(nw_device_spec, device_inventory):
    log.info('create default deployment')
    nw_devices = SetManager(set(nw_device_spec))
    inventory = InventoryManager(device_inventory)
    # TODO: use dict and add latency & bandwidth
    links = []
    # attach devices to HomeIotGW
    network_device = nw_devices.get('HomeIotGW')
    device = inventory.pop(DeviceCategory.SENSOR, Device.THERMAL)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.SENSOR, Device.THERMAL)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.SENSOR, Device.CAMERA)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    # attach devices to HomeRouter
    network_device = nw_devices.get('HomeRouter')
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.T2_MICRO)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.T3_LARGE)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    # attach devices to CloudSwitch
    network_device = nw_devices.get('CloudSwitch')
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.T2_MICRO)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.T3_LARGE)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    device = inventory.pop(DeviceCategory.PROCESSOR, Device.P3_2XLARGE)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    # attach devices to BaseStation
    network_device = nw_devices.get('BaseStation')
    device = inventory.pop(DeviceCategory.ACTUATOR, Device.PHONE)
    links.append(gen_link_str(device, network_device))
    links.append(gen_link_str(network_device, device))
    return links


def create_default_topo():
    log.info('create default topo')
    device_spec = _create_default_network_devices()
    nw_links = _create_default_network_links(set(device_spec))
    device2nw_links = _create_default_deployment(
        set(device_spec), create_default_inventory())
    return device_spec, nw_links, device2nw_links


def export_all_data():
    device_spec, device_inventory = create_default_device_data()
    json_utils.export_bundle(
        'config_default/device_data.json',
        device_spec=device_spec,
        device_inventory=device_inventory)
    _device_spec, _device_inventory = json_utils.import_bundle(
        common_utils.get_file_path('config_default/device_data.json'),
        'device_spec',
        'device_inventory',
    )
    assert _device_spec == device_spec
    assert _device_inventory == device_inventory

    task_info, edge_info, src_map, dst_map = create_default_task_graph()
    json_utils.export_bundle(
        common_utils.get_file_path('config_default/task_graph.json'),
        task_info=task_info,
        edge_info=edge_info,
        src_map=src_map,
        dst_map=dst_map,
    )
    _task_info, _edge_info, _src_map, _dst_map = json_utils.import_bundle(
        common_utils.get_file_path('config_default/task_graph.json'),
        'task_info',
        'edge_info',
        'src_map',
        'dst_map',
    )
    assert _task_info == task_info
    assert _edge_info == edge_info
    assert _src_map == src_map, (
        '\n{}\n!=\n{}'.format(_src_map, src_map))
    assert _dst_map == dst_map

    nw_device_spec, nw_links, device_links = create_default_topo()
    json_utils.export_bundle(
        common_utils.get_file_path('config_default/topo.json'),
        nw_device_spec=nw_device_spec,
        nw_links=nw_links,
        device_links=device_links,
    )
    _nw_device_spec, _nw_links, _device_links = json_utils.import_bundle(
        common_utils.get_file_path('config_default/topo.json'),
        'nw_device_spec',
        'nw_links',
        'device_links',
    )
    assert _nw_device_spec == nw_device_spec
    assert _nw_links == nw_links
    assert _device_links == device_links
