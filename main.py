from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging


logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(funcName)s: %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class SubArgsManager(object):
    def __init__(self, subparser):
        self.subparser = subparser

    def visualize_topology(self, required=False):
        self.subparser.add_argument(
            '-v',
            '--visualize',
            type=bool,
            dest='is_plot',
            default=False,
            required=required,
            help='plot topology')


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
    def create_topology(args):

        from placethings.topology import Topology

        is_plot = args.is_plot

        topo = Topology.create_default()
        if is_plot:
            Topology.plot(topo)

    @staticmethod
    def place_things(args):

        from placethings.ilp_solver import Problems

        Problems.place_things()


def main():
    args_manager = ArgsManager()

    name = 'create_topology'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='generate network topology')
    subargs_manager.visualize_topology(required=False)

    name = 'place_things'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='compute placement')
    subargs_manager.visualize_topology(required=False)

    args = args_manager.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
