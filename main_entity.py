from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

from placethings.demo.entity import test_entity
from placethings.demo.entity.base_server import ServerGen, Entity
from placethings.utils.common_utils import update_rootlogger

update_rootlogger()
log = logging.getLogger()


class SubArgsManager(object):
    def __init__(self, subparser):
        self.subparser = subparser

    def name(self, required=False):
        self.subparser.add_argument(
            '-n',
            '--name',
            type=str,
            dest='name',
            default=None,
            required=required,
            help=('name')
        )

    def address(self, required=False):
        self.subparser.add_argument(
            '-a',
            '--address',
            type=str,
            dest='address',
            default=None,
            required=required,
            help=('address (ip:port). e.g. 10.11.12.13:1234')
        )

    def exectime(self, required=False):
        self.subparser.add_argument(
            '-t',
            '--exectime',
            type=int,
            dest='exectime',
            default=None,
            required=required,
            help=('exectime (ms)')
        )

    def testcase(self, required=False):
        self.subparser.add_argument(
            '-tc',
            '--testcase',
            type=str,
            dest='testcase',
            default=None,
            required=required,
            help=('testcase name')
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
    def run_agent(args):
        name = args.name
        ip, port = args.address.split(':')
        port = int(port)
        update_rootlogger(name, is_log_to_file=True)
        ServerGen.start_server(name, Entity.AGENT, ip, port)

    @staticmethod
    def run_fileserver(args):
        name = args.name
        ip, port = args.address.split(':')
        port = int(port)
        update_rootlogger(name, is_log_to_file=True)
        ServerGen.start_server(name, Entity.FILESERVER, ip, port)

    @staticmethod
    def run_task(args):
        name = args.name
        ip, port = args.address.split(':')
        port = int(port)
        exec_time_ms = args.exectime
        next_task_ip = None
        next_task_port = None
        update_rootlogger(name, is_log_to_file=True)
        ServerGen.start_server(
            name, Entity.TASK, ip, port,
            exec_time_ms, next_task_ip, next_task_port)

    @staticmethod
    def run_manager(args):
        case_name = args.testcase
        update_rootlogger('manager', is_log_to_file=True)
        getattr(test_entity, case_name)()

    @staticmethod
    def stop_server(args):
        ip, port = args.address.split(':')
        ServerGen.stop_server(ip, int(port))


def main():
    args_manager = ArgsManager()

    name = 'run_agent'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_agent')
    subargs_manager.name(required=True)
    subargs_manager.address(required=True)

    name = 'run_fileserver'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_fileserver')
    subargs_manager.name(required=True)
    subargs_manager.address(required=True)

    name = 'stop_server'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='stop_server')
    subargs_manager.name(required=True)
    subargs_manager.address(required=True)

    name = 'run_task'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_task')
    subargs_manager.name(required=True)
    subargs_manager.address(required=True)
    subargs_manager.exectime(required=True)

    name = 'run_manager'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_manager')
    subargs_manager.testcase(required=True)

    args = args_manager.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
