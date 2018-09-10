from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

from placethings import ilp_solver
from placethings.definition import Unit
from placethings.config import config_factory
from placethings.graph_gen import graph_factory


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
            dest='is_export',
            default=False,
            required=required,
            help='export graph and data')

    def config(self, required=False):
        self.subparser.add_argument(
            '-c',
            '--config',
            type=str,
            dest='config_name',
            default='config_default',
            required=required,
            help=(
                'gen graph base on confiig files. '
                'If not specified, use config_dafult')
        )


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
        config_name = args.config_name
        graph_factory.gen_topo_graph(config_name, is_export=True)

    @staticmethod
    def create_taskgraph(args):
        config_name = args.config_name
        graph_factory.gen_task_graph(config_name, is_export=True)

    @staticmethod
    def create_devicegraph(args):
        config_name = args.config_name
        graph_factory.gen_device_graph(config_name, is_export=True)

    @staticmethod
    def export_all_graph(args):
        config_name = args.config_name
        graph_factory.gen_device_graph(config_name, is_export=True)
        graph_factory.gen_task_graph(config_name, is_export=True)
        graph_factory.gen_topo_graph(config_name, is_export=True)

    @staticmethod
    def place_things(args):
        config_name = args.config_name
        is_export = args.is_export
        Gt = graph_factory.gen_task_graph(config_name, is_export)
        Gd = graph_factory.gen_device_graph(config_name, is_export)
        ilp_solver.place_things(Unit.sec(2), Gt, Gd, is_export)

    @staticmethod
    def export_default_config(args):
        config_factory.export_default_config()


def main():
    args_manager = ArgsManager()

    name = 'create_topograph'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='generate network topology')
    subargs_manager.config(required=False)

    name = 'create_taskgraph'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='generate task graph')
    subargs_manager.config(required=False)

    name = 'create_devicegraph'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='generate network graph')
    subargs_manager.config(required=False)

    name = 'export_all_graph'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='export all config to json')
    subargs_manager.config(required=False)

    name = 'place_things'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='compute placement')
    subargs_manager.visualize(required=False)
    subargs_manager.config(required=False)

    name = 'export_default_config'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='export all default config to json')

    args = args_manager.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
