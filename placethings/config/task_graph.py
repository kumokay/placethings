from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.config import default_def
from placethings.config.common import LinkHelper, SetManager
from placethings.definition import Device, Flavor, GtInfo, Hardware, Unit
from placethings.utils import common_utils, graph_utils, json_utils


log = logging.getLogger()


def _create_default_node_info():
    """
    Returns:
        node_info (dict): {node_name (str): node_data (dict)}, where
            node_data = { data_name (GtInfo): data (any) }
    """
    log.info('create default node (task) info')
    tasks = SetManager(default_def.DEFAULT_TASKS)
    node_info = {
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
    return node_info


def _create_default_edge_info():
    """
    Returns:
        edge_info (dict): { 'node1 -> node2' (str): edge_data (dict)}, where
            edge_data = { data_name (GtInfo): data (any) }
    """
    log.info('create default edge info')
    tasks = SetManager(default_def.DEFAULT_TASKS)
    edge_info = {}
    t1 = tasks.get('task_thermal_loc1')
    t2 = tasks.get('task_getAvgTemperature')
    edge_info[LinkHelper.get_edge(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.kbyte(1),
    }
    t1 = tasks.get('task_thermal_loc2')
    t2 = tasks.get('task_getAvgTemperature')
    edge_info[LinkHelper.get_edge(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.kbyte(1),
    }
    t1 = tasks.get('task_getAvgTemperature')
    t2 = tasks.get('task_checkAbnormalEvent')
    edge_info[LinkHelper.get_edge(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.byte(1),
    }
    t1 = tasks.get('task_camera')
    t2 = tasks.get('task_findObject')
    edge_info[LinkHelper.get_edge(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.mbyte(10),
    }
    t1 = tasks.get('task_findObject')
    t2 = tasks.get('task_checkAbnormalEvent')
    edge_info[LinkHelper.get_edge(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.byte(10),
    }
    t1 = tasks.get('task_checkAbnormalEvent')
    t2 = tasks.get('task_sentNotificatoin')
    edge_info[LinkHelper.get_edge(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.byte(1),
    }
    t1 = tasks.get('task_sentNotificatoin')
    t2 = tasks.get('task_broadcast')
    edge_info[LinkHelper.get_edge(t1, t2)] = {
        GtInfo.TRAFFIC: Unit.byte(1),
    }
    return edge_info


def create_default_task_graph():
    node_info = _create_default_node_info()
    edge_info = _create_default_edge_info()
    graph = graph_utils.gen_graph(node_info, edge_info)
    return graph


def export_data():
    node_info = _create_default_node_info()
    edge_info = _create_default_edge_info()
    json_utils.export_bundle(
        'config_default/task_graph.json',
        node_info=node_info,
        edge_info=edge_info)
    _node_info, _edge_info = import_data()
    assert _node_info == node_info
    assert _edge_info == edge_info


def import_data():
    node_info, edge_info = json_utils.import_bundle(
        common_utils.get_file_path('config_default/task_graph.json'),
        'node_info',
        'edge_info',
    )
    return node_info, edge_info
