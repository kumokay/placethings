from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

from placethings import definition, ilp_solver, utils
from placethings.network_graph import NetworkGraph
from placethings.task_graph import TaskGraph
from placethings.topology import TopoGraph


logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(funcName)s: %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class SubArgsManager(object):
    def __init__(self, subparser):
        self.subparser = subparser

    def visualize(self, required=False):
        self.subparser.add_argument(
            '-v',
            '--visualize',
            type=bool,
            dest='is_plot',
            default=False,
            required=required,
            help='plot graph')


class ArgsManager(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='PROG')
        self.subparsers = self.parser.add_subparsers(help='sub-command help')

    def add_subparser(self, option_name, func, help='help'):
        subparser = self.subparsers.add_parser(
            option_name,
            help=help)
        subparser.set_defaults(func=func)
        return SubArgsManager(subparser)

    def parse_args(self):
        return self.parser.parse_args()


class FuncManager(object):

    @staticmethod
    def create_topograph(args):
        is_plot = args.is_plot
        switches = TopoGraph.create_default_switch_list()
        devices = list(NetworkGraph.create_default_device_info())
        topo = TopoGraph.create_default_topo(switches, devices)
        if is_plot:
            utils.show_plot(
                topo,
                with_edge=True,
                which_edge_label=definition.GnInfo.LATENCY)

    @staticmethod
    def create_taskgraph(args):
        is_plot = args.is_plot
        graph = TaskGraph.create_default_graph()
        if is_plot:
            utils.show_plot(graph)

    @staticmethod
    def create_networkgraph(args):
        is_plot = args.is_plot
        graph = NetworkGraph.create_default_graph()
        if is_plot:
            utils.show_plot(
                graph,
                with_edge=True,
                which_edge_label=definition.GdInfo.LATENCY)

    @staticmethod
    def place_things(args):
        src_map, dst_map, task_info, edge_info = (
            TaskGraph.create_default_data())
        Gt = TaskGraph.create(src_map, dst_map, task_info, edge_info)
        Gd = NetworkGraph.create_default_graph()
        ilp_solver.place_things(utils.Unit.sec(10), Gt, Gd, src_map, dst_map)


def main():
    args_manager = ArgsManager()

    name = 'create_topograph'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='generate network topology')
    subargs_manager.visualize(required=False)

    name = 'create_taskgraph'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='generate task graph')
    subargs_manager.visualize(required=False)

    name = 'create_networkgraph'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='generate network graph')
    subargs_manager.visualize(required=False)

    name = 'place_things'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='compute placement')
    subargs_manager.visualize(required=False)

    args = args_manager.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
