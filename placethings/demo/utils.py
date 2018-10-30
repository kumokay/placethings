from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings import ilp_solver
from placethings.config import device_data, nw_device_data, task_data
from placethings.config.common import LinkHelper
from placethings.definition import GnInfo
from placethings.graph_gen import device_graph, graph_factory
from placethings.config.config_factory import FileHelper


log = logging.getLogger()


class ConfigDataHelper(object):
    _DEFAULT_CONFIG = 'config_default'

    def __init__(self, config_name=None, is_export=False):
        if not config_name:
            config_name = self._DEFAULT_CONFIG
        self.config_name = config_name
        self.is_export = is_export
        self.update_id = -1
        # get device data and topo data
        dev_file = FileHelper.gen_config_filepath(config_name, 'device_data')
        nw_file = FileHelper.gen_config_filepath(config_name, 'nw_device_data')
        spec, inventory, links = device_data.import_data(dev_file)
        nw_spec, nw_inventory, nw_links = nw_device_data.import_data(nw_file)
        self.dev_spec = spec
        self.dev_inventory = inventory
        self.dev_links = links
        self.nw_spec = nw_spec
        self.nw_inventory = nw_inventory
        self.nw_links = nw_links
        # get task data
        task_file = FileHelper.gen_config_filepath(config_name, 'task_data')
        task_mapping, task_links, task_info = task_data.import_data(task_file)
        self.task_mapping = task_mapping
        self.task_links = task_links
        self.task_info = task_info
        # graphs
        self.topo = None
        self.topo_device_graph = None
        self.Gt = None
        self.Gd = None
        self.G_map = None
        self.result_mapping = None
        self.max_latency_log = []
        self.max_latency_static_log = []

    def init_task_graph(self):
        log.info('init task graph')
        Gt = graph_factory.gen_task_graph(
            self.config_name,
            is_export=self.is_export)
        self.Gt = Gt

    def update_topo_device_graph(self):
        self.update_id += 1
        log.info('round {}: update topo device graph'.format(self.update_id))
        topo, topo_device_graph, Gd = device_graph.create_topo_device_graph(
            self.dev_spec, self.dev_inventory, self.dev_links,
            self.nw_spec, self.nw_inventory, self.nw_links,
            is_export=self.is_export, export_suffix=self.update_id)
        self.topo = topo
        self.topo_device_graph = topo_device_graph
        self.Gd = Gd

    def update_task_map(self):
        G_map, result_mapping = ilp_solver.place_things(
            self.Gt, self.Gd,
            is_export=self.is_export, export_suffix=self.update_id)
        self.G_map = G_map
        self.result_mapping = result_mapping
        if self.update_id == 0:
            # init update
            self.init_result_mapping = result_mapping
        log.info('mapping result: {}'.format(result_mapping))

    def update_max_latency_log(self):
        max_latency = ilp_solver.get_max_latency(
            self.Gt, self.Gd, self.result_mapping)
        self.max_latency_log.append(max_latency)
        max_latency_static = ilp_solver.get_max_latency(
            self.Gt, self.Gd, self.init_result_mapping)
        self.max_latency_static_log.append(max_latency_static)

    def get_max_latency_log(self):
        return self.max_latency_log, self.max_latency_static_log

    def get_graphs(self):
        return self.topo, self.topo_device_graph, self.Gd, self.G_map

    def _gen_link(src, dst):
        return '{} -> {}'.format

    @staticmethod
    def _update_link_latency(links_dict, n1, n2, latency):
        edge_str = LinkHelper.get_edge(n1, n2)
        latency_before = links_dict[edge_str][GnInfo.LATENCY]
        log.info('update link latency {}: {} => {}'.format(
            edge_str, latency_before, latency))
        # update link latency
        edge_str = LinkHelper.get_edge(n1, n2)
        links_dict[edge_str][GnInfo.LATENCY] = latency
        edge_str = LinkHelper.get_edge(n2, n1)
        links_dict[edge_str][GnInfo.LATENCY] = latency

    @staticmethod
    def _update_link_dst(links_dict, n1, n2, new_n2, new_latency):
        log.info('update link {n1} <-> {n2} => {n1} <-> {new_n2}'.format(
            n1=n1, n2=n2, new_n2=new_n2))
        # delete link
        edge_str = LinkHelper.get_edge(n1, n2)
        del links_dict[edge_str]
        edge_str = LinkHelper.get_edge(n2, n1)
        del links_dict[edge_str]
        # add link
        edge_str = LinkHelper.get_edge(n1, new_n2)
        links_dict[edge_str] = {
            GnInfo.LATENCY: new_latency}
        edge_str = LinkHelper.get_edge(new_n2, n1)
        links_dict[edge_str] = {
            GnInfo.LATENCY: new_latency}

    def update_dev_link_latency(self, dev, nw_dev, latency):
        """
        update device <-> network_dev link latency.
            e.g. change lantency of 'PHONE.0 -> BB_AP.0' from 3ms to 30 ms
        """
        self._update_link_latency(self.dev_links, dev, nw_dev, latency)

    def update_nw_link_latency(self, nw_dev1, nw_dev2, latency):
        """
        update network_dev <-> network_dev link latency.
            e.g. change lantency of 'BB_SWITCH.0 -> BB_AP.0' from 3ms to 30 ms
        """
        self._update_link_latency(self.nw_links, nw_dev1, nw_dev2, latency)

    def update_dev_link(self, dev, nw_dev, new_nw_dev, new_latency):
        """
        update device <-> network_dev link.
            e.g. change 'PHONE.0 -> BB_AP.0' to 'PHONE.0 -> BB_AP.1'
        """
        self._update_link_dst(
            self.dev_links, dev, nw_dev, new_nw_dev, new_latency)

    def update_nw_link(self, nw_dev1, nw_dev2, new_nw_dev2, new_latency):
        """
        update device <-> network_dev link.
            e.g. change 'PHONE.0 -> BB_AP.0' to 'PHONE.0 -> BB_AP.1'
        """
        self._update_link_dst(
            self.nw_links, nw_dev1, nw_dev2, new_nw_dev2, new_latency)
