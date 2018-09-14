from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import iteritems
import logging
import time

from placethings import ilp_solver
from placethings.config import device_data, nw_device_data
from placethings.definition import (
    GnInfo, Unit, GdInfo, GtInfo, DeviceCategory, Device)
from placethings.graph_gen import graph_factory, device_graph
from placethings.config.config_factory import FileHelper
from placethings.netgen.network import ControlPlane, DataPlane
from placethings.demo.entity.sensor import SensorType
from placethings.demo.entity.manager import Manager
from placethings.demo.utils import AddressManager


log = logging.getLogger()


_DEFAULT_CONFIG = 'config_default'


def _gen_topo_device_graph(config_name, is_export):
    # generate topo device graph
    dev_file = FileHelper.gen_config_filepath(config_name, 'device_data')
    nw_file = FileHelper.gen_config_filepath(config_name, 'nw_device_data')
    spec, inventory, links = device_data.import_data(dev_file)
    nw_spec, nw_inventory, nw_links = nw_device_data.import_data(nw_file)
    topo_graph, topo_device_graph, Gd = device_graph.create_topo_device_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links, is_export)
    return topo_graph, topo_device_graph, Gd


def _gen_agent_name(device_name):
    return 'A-{}'.format(device_name)


def test_deploy_default(config_name=None, is_export=True):
    if not config_name:
        config_name = _DEFAULT_CONFIG
    # generate input topo, device task data
    Gt = graph_factory.gen_task_graph(config_name, is_export)
    topo_graph, topo_device_graph, Gd = _gen_topo_device_graph(
        config_name, is_export)
    G_map = ilp_solver.place_things(Gt, Gd, is_export)
    # simulate network
    control_plane = ControlPlane(topo_device_graph)
    control_plane.addManagerDevice('Manager', 'HOME_ROUTER.0')
    data_plane = DataPlane(topo_device_graph)
    # TODO: rewrite



    net.start()
    # net.validate()
    # install manager / agents / tasks
    net.addHost('Manager')
    net.addLink('Manager', 'HOME_ROUTER.0', )
    _PROG_DIR = '/home/kumokay/github/placethings'
    addr_manager = AddressManager(net)
    # run agents on all processors
    cmd_template = (
        'cd {progdir} && python main_entity.py run_agent '
        '-a {ip}:{port} -n {name}')
    for device_name in Gd.nodes():
        device_cat = Gd.node[device_name][GdInfo.DEVICE_CAT]
        if device_cat == DeviceCategory.PROCESSOR:
            name = _gen_agent_name(device_name)
            ip, port = addr_manager.get_task_address(name, device_name)
            command = cmd_template.format(
                progdir=_PROG_DIR,
                ip=ip,
                port=port,
                name=name)
            net.run_cmd(device_name, command, async=True)
    # deploy tasks
    cmd_actuator_template = (
        'cd {progdir} && python main_entity.py run_actuator '
        '-a {ip}:{port} -n {name}')
    cmd_sensor_template = (
        'cd {progdir} && python main_entity.py run_sensor '
        '-a {ip}:{port} -n {name} -st {sensor_type} -ra {next_ip}:{next_port}')
    cmd_task_template = (
        'cd {progdir} && python main_entity.py run_task '
        '-a {ip}:{port} -n {name} -t {exectime} -ra {next_ip}:{next_port}')
    for task_name in G_map.nodes():
        device_name = G_map.node[task_name][GtInfo.CUR_DEVICE]
        device_cat = Gd.node[device_name][GdInfo.DEVICE_CAT]
        exectime = G_map.node[task_name][GtInfo.CUR_LATENCY]
        name = task_name
        ip, port = addr_manager.get_task_address(name, device_name)
        if device_cat == DeviceCategory.ACTUATOR:
            command = cmd_actuator_template.format(
                progdir=_PROG_DIR,
                ip=ip,
                port=port,
                name=name)
            net.run_cmd(device_name, command, async=True)
        elif device_cat == DeviceCategory.SENSOR:
            device_type = Gd.node[device_name][GdInfo.DEVICE_TYPE]
            if device_type == Device.CAMERA:
                sensor_type = SensorType.CAMERA
            elif device_type == Device.THERMAL:
                sensor_type = SensorType.THERMAL
            else:
                assert False, 'undefined sensor'
            next_task_list = list(G_map.successors(task_name))
            assert len(next_task_list) == 1, 'support 1 successor now'
            next_task = next_task_list[0]
            next_device = G_map.node[next_task][GtInfo.CUR_DEVICE]
            next_ip, next_port = addr_manager.get_task_address(
                next_task, next_device)
            command = cmd_sensor_template.format(
                progdir=_PROG_DIR,
                ip=ip,
                port=port,
                name=name,
                sensor_type=sensor_type,
                next_ip=next_ip,
                next_port=next_port)
            net.run_cmd(device_name, command, async=True)
        elif device_cat == DeviceCategory.PROCESSOR:
            next_task_list = list(G_map.successors(task_name))
            assert len(next_task_list) == 1, 'support 1 successor now'
            next_task = next_task_list[0]
            next_device = G_map.node[next_task][GtInfo.CUR_DEVICE]
            next_ip, next_port = addr_manager.get_task_address(
                next_task, next_device)
            command = cmd_task_template.format(
                progdir=_PROG_DIR,
                ip=ip,
                port=port,
                name=name,
                exectime=exectime,
                next_ip=next_ip,
                next_port=next_port)
            net.run_cmd('Manager', command)
    # running
    time.sleep(20)
    # cleanup
    cmd_template = (
        'cd {progdir} && python main_entity.py stop_server -a {ip}:{port}')
    for entity_name, addr_info in iteritems(addr_manager.get_address_book()):
        device_name, ip, port = addr_info
        command = cmd_template.format(
            progdir=_PROG_DIR,
            ip=ip,
            port=port)
        net.run_cmd(device_name, command, async=True)
    net.stop()


def test_deploy_basic(config_name=None, is_export=False):
    if not config_name:
        config_name = _DEFAULT_CONFIG
    # generate topo device graph
    dev_file = FileHelper.gen_config_filepath(config_name, 'device_data')
    nw_file = FileHelper.gen_config_filepath(config_name, 'nw_device_data')
    spec, inventory, links = device_data.import_data(dev_file)
    nw_spec, nw_inventory, nw_links = nw_device_data.import_data(nw_file)
    topo_device_graph, _device_graph = device_graph.create_topo_device_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links, is_export)
    net = NetGen.create(topo_device_graph)
    net.start()
    net.validate()

    command_switch_dir = 'cd /home/kumokay/github/placethings'
    port = 18800
    all_ips = set()

    device = 'PHONE.0'
    ip = net.get_device_ip(device)
    port += 1
    command_start = 'python main_entity.py run_agent -a {}:{}'.format(
        ip, port)
    net.run_cmd(device, command_switch_dir, async=False)
    net.run_cmd(device, command_start, async=True)
    all_ips.add((ip, port))

    device = 'CAMERA.0'
    ip = net.get_device_ip(device)
    port += 1
    command_start = 'python main_entity.py run_task -a {}:{} -t {}'.format(
        ip, port, 5000)
    net.run_cmd(device, command_switch_dir, async=False)
    net.run_cmd(device, command_start, async=True)
    all_ips.add((ip, port))

    device = 'T2_MICRO.0'
    port += 1
    ip = net.get_device_ip(device)
    command_start = 'python main_entity.py run_agent -a {}:{}'.format(
        ip, port)
    net.run_cmd(device, command_switch_dir, async=False)
    net.run_cmd(device, command_start, async=True)
    all_ips.add((ip, port))

    # cleanup
    for ip, port in all_ips:
        device = 'T2_MICRO.1'
        command_start = 'python main_entity.py stop_server -a {}:{}'.format(
            ip, port)
        net.run_cmd(device, command_switch_dir, async=False)
        net.run_cmd(device, command_start, async=False)
        all_ips.add((ip, port))
    net.stop()


def test_netgen(config_name=None, is_export=False):
    if not config_name:
        config_name = _DEFAULT_CONFIG
    # generate topo device graph
    dev_file = FileHelper.gen_config_filepath(config_name, 'device_data')
    nw_file = FileHelper.gen_config_filepath(config_name, 'nw_device_data')
    spec, inventory, links = device_data.import_data(dev_file)
    nw_spec, nw_inventory, nw_links = nw_device_data.import_data(nw_file)
    topo_device_graph, _device_graph = device_graph.create_topo_device_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links, is_export)
    net = NetGen.create(topo_device_graph)
    net.start()
    net.validate()
    net.stop()


def test_config(config_name=None, is_export=False):
    if not config_name:
        config_name = _DEFAULT_CONFIG
    Gt = graph_factory.gen_task_graph(config_name, is_export)
    Gd = graph_factory.gen_device_graph(config_name, is_export)
    ilp_solver.place_things(Gt, Gd, is_export)


def test_dynamic(config_name=None, is_export=False):
    if not config_name:
        config_name = _DEFAULT_CONFIG
    # generate device graph
    dev_file = FileHelper.gen_config_filepath(config_name, 'device_data')
    nw_file = FileHelper.gen_config_filepath(config_name, 'nw_device_data')
    spec, inventory, links = device_data.import_data(dev_file)
    nw_spec, nw_inventory, nw_links = nw_device_data.import_data(nw_file)
    Gd = device_graph.create_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links, is_export)
    # generate task graph
    Gt = graph_factory.gen_task_graph(config_name, is_export)
    Gt = ilp_solver.place_things(Gt, Gd, is_export)
    update_id = 0
    # update device graph
    update_id += 1
    log.info('update round {}'.format(update_id))
    suffix = '_update{}'.format(update_id)
    del links['PHONE.0 -> BB_AP.0']
    del links['BB_AP.0 -> PHONE.0']
    links['PHONE.0 -> HOME_IOTGW.0'] = {
        GnInfo.LATENCY: Unit.ms(3),
    }
    links['HOME_IOTGW.0 -> PHONE.0'] = {
        GnInfo.LATENCY: Unit.ms(3),
    }
    Gd = device_graph.create_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links,
        is_export, export_suffix='_update{}'.format(update_id))
    Gt = ilp_solver.place_things(Gt, Gd, is_export, export_suffix=suffix)
    # update device graph
    update_id += 1
    log.info('update round {}'.format(update_id))
    suffix = '_update{}'.format(update_id)
    nw_links['BB_SWITCH.0 -> CLOUD_SWITCH.0'][GnInfo.LATENCY] = Unit.sec(5)
    nw_links['CLOUD_SWITCH.0 -> BB_SWITCH.0'][GnInfo.LATENCY] = Unit.sec(5)
    Gd = device_graph.create_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links,
        is_export, export_suffix=suffix)
    Gt = ilp_solver.place_things(Gt, Gd, is_export, export_suffix=suffix)
    # update device graph
    update_id += 1
    log.info('update round {}'.format(update_id))
    suffix = '_update{}'.format(update_id)
    del links['PHONE.0 -> HOME_IOTGW.0']
    del links['HOME_IOTGW.0 -> PHONE.0']
    links['PHONE.0 -> BB_AP.0'] = {
        GnInfo.LATENCY: Unit.ms(3),
    }
    links['BB_AP.0 -> PHONE.0'] = {
        GnInfo.LATENCY: Unit.ms(3),
    }
    Gd = device_graph.create_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links,
        is_export, export_suffix='_update{}'.format(update_id))
    Gt = ilp_solver.place_things(Gt, Gd, is_export, export_suffix=suffix)
    # update device graph
    update_id += 1
    log.info('update round {}'.format(update_id))
    suffix = '_update{}'.format(update_id)
    nw_links['BB_SWITCH.0 -> CLOUD_SWITCH.0'][GnInfo.LATENCY] = Unit.ms(5)
    nw_links['CLOUD_SWITCH.0 -> BB_SWITCH.0'][GnInfo.LATENCY] = Unit.ms(5)
    Gd = device_graph.create_graph(
        spec, inventory, links, nw_spec, nw_inventory, nw_links,
        is_export, export_suffix=suffix)
    Gt = ilp_solver.place_things(Gt, Gd, is_export, export_suffix=suffix)
