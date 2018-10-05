from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import random

from placethings.demo.utils import ConfigDataHelper
from placethings.demo.base_test import BaseTestCase
from placethings.definition import Unit

log = logging.getLogger()


class TestPhase1(BaseTestCase):
    @staticmethod
    def _simulate(topo_device_graph, Gd, G_map):
        pass

    @classmethod
    def test(
            cls, config_name, is_export=False,
            is_update_map=True, is_simulate=False):
        assert config_name == 'config_ddflow_phase1'
        cfgHelper = ConfigDataHelper(config_name, is_export)
        cfgHelper.init_task_graph()
        cfgHelper.update_topo_device_graph()
        cfgHelper.update_task_map()
        cfgHelper.update_max_latency_log()
        topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
        if is_simulate:
            cls._simulate(topo_device_graph, Gd, G_map)
        all_devices = [
            'P3_2XLARGE.0',
            'T3_LARGE.0',
            'T2_MICRO.0']
        all_sws = [
            'CENTER_SWITCH.0',
            'FIELD_SWITCH.0',
            'FIELD_SWITCH.1',
            'BB_SWITCH.0',
            'BB_SWITCH.1',
            'BB_SWITCH.2']
        update_id = -1
        for i in range(1, 50):
            update_id += 1
            log.info('=== update {}: dev-nw_dev link ==='.format(update_id))
            edges = list(topo_device_graph.edges())
            [dev] = random.sample(all_devices, 1)
            [nw_dev] = random.sample(all_sws, 1)
            while (dev, nw_dev) not in edges:
                [dev] = random.sample(all_devices, 1)
                [nw_dev] = random.sample(all_sws, 1)
            latency = Unit.ms(random.randint(5, 3000))
            cfgHelper.update_dev_link_latency(dev, nw_dev, latency)
            cfgHelper.update_topo_device_graph()
            if is_update_map:
                cfgHelper.update_task_map()
            cfgHelper.update_max_latency_log()
            topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
            if is_simulate:
                cls._simulate(topo_device_graph, Gd, G_map)
            log.info('=== update {}: nw_dev-nw_dev link ==='.format(update_id))
            edges = list(topo_device_graph.edges())
            [nw_dev1, nw_dev2] = random.sample(all_sws, 2)
            while (nw_dev1, nw_dev2) not in edges:
                [nw_dev1, nw_dev2] = random.sample(all_sws, 2)
            latency = Unit.ms(random.randint(5, 200))
            cfgHelper.update_nw_link_latency(nw_dev1, nw_dev2, latency)
            cfgHelper.update_topo_device_graph()
            if is_update_map:
                cfgHelper.update_task_map()
            cfgHelper.update_max_latency_log()
            topo, topo_device_graph, Gd, G_map = cfgHelper.get_graphs()
            if is_simulate:
                cls._simulate(topo_device_graph, Gd, G_map)
        latency_dynamic, latency_static = cfgHelper.get_max_latency_log()
        log.info('static\tdynamic\tdiff')
        for t1, t2 in zip(latency_static, latency_dynamic):
            log.info('{}\t{}\t{}'.format(t1, t2, t2 - t1))


class TestPhase2(BaseTestCase):
    @staticmethod
    def _simulate(topo_device_graph, Gd, G_map):
        pass

    @classmethod
    def test(
            cls, config_name, is_export=False,
            is_update_map=False, is_simulate=False):
        assert config_name == 'config_ddflow_phase2'
        # TODO: clean this shit
        cfg1 = '{}.1'.format(config_name)
        cfg2 = '{}.2'.format(config_name)
        cfgHelper = ConfigDataHelper(cfg1, is_export)
        cfgHelper.init_task_graph()
        cfgHelper.update_topo_device_graph()
        cfgHelper.update_task_map()
        cfgHelper.update_max_latency_log()
        cfgHelper2 = ConfigDataHelper(cfg2, is_export)
        cfgHelper2.init_task_graph()
        cfgHelper2.update_topo_device_graph()
        cfgHelper2.update_task_map()
        cfgHelper2.update_max_latency_log()
        all_mobiles = [
            'CAMERA.0']
        all_sws = [
            'BB_SWITCH.0',
            'BB_SWITCH.1',
            'BB_SWITCH.2']
        all_aps = [
            'BB_AP.0',
            'BB_AP.1',
            'BB_AP.2']
        update_id = -1
        for i in range(1, 100):
            update_id += 1
            log.info('=== update {}: mobile-ap link ==='.format(update_id))
            dev = random.sample(all_mobiles, 1)[0]
            _, topo_device_graph, _, _ = cfgHelper.get_graphs()
            edges = list(topo_device_graph.edges(dev))
            assert len(edges) == 1
            nw_dev = edges[0][1]
            assert nw_dev in all_aps, '{} not in {}'.format(nw_dev, all_aps)
            new_nw_dev = random.sample(all_aps, 1)[0]
            new_latency = Unit.ms(random.randint(1, 20))
            cfgHelper.update_dev_link(dev, nw_dev, new_nw_dev, new_latency)
            cfgHelper2.update_dev_link(dev, nw_dev, new_nw_dev, new_latency)
            log.info('=== update {}: nw_dev-nw_dev link ==='.format(update_id))
            _, topo_device_graph, _, _ = cfgHelper.get_graphs()
            edges = list(topo_device_graph.edges())
            [nw_dev1, nw_dev2] = random.sample(all_sws + all_aps, 2)
            while (nw_dev1, nw_dev2) not in edges:
                [nw_dev1, nw_dev2] = random.sample(all_sws + all_aps, 2)
            latency = Unit.ms(random.randint(5, 200))
            cfgHelper.update_nw_link_latency(nw_dev1, nw_dev2, latency)
            cfgHelper2.update_nw_link_latency(nw_dev1, nw_dev2, latency)
            log.info('=== update {}: ap-ap link ==='.format(update_id))
            _, topo_device_graph, _, _ = cfgHelper2.get_graphs()
            edges = list(topo_device_graph.edges())
            [nw_dev1, nw_dev2] = random.sample(all_aps, 2)
            while (nw_dev1, nw_dev2) not in edges:
                [nw_dev1, nw_dev2] = random.sample(all_aps, 2)
            latency = Unit.ms(random.randint(25, 100))
            cfgHelper2.update_nw_link_latency(nw_dev1, nw_dev2, latency)
            # update graph and log
            cfgHelper.update_topo_device_graph()
            cfgHelper2.update_topo_device_graph()
            if is_update_map:
                cfgHelper.update_task_map()
                cfgHelper2.update_task_map()
            cfgHelper.update_max_latency_log()
            cfgHelper2.update_max_latency_log()
        _, latency_static = cfgHelper.get_max_latency_log()
        _, latency_static2 = cfgHelper2.get_max_latency_log()
        log.info('static\tdynamic\tdiff')
        for t1, t2 in zip(latency_static, latency_static2):
            log.info('{}\t{}\t{}'.format(t1, t2, t2 - t1))
