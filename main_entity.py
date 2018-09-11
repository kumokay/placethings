from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

from placethings.demo.entity import test_entity
from placethings.demo.entity.baseserver import ServerGen, Entity


logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(funcName)s: %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class SubArgsManager(object):
    def __init__(self, subparser):
        self.subparser = subparser

    def address(self, required=False):
        self.subparser.add_argument(
            '-a',
            '--address',
            type=str,
            dest='address',
            default=None,
            required=required,
            help=('address')
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
        ip, port = args.address.split(':')
        agent = ServerGen.create(Entity.AGENT)
        agent.start(ip, int(port))

    @staticmethod
    def run_fileserver(args):
        ip, port = args.address.split(':')
        fileserver = ServerGen.create(Entity.FILESERVER)
        fileserver.start(ip, int(port))

    @staticmethod
    def run_manager(args):
        case_name = args.testcase
        getattr(test_entity, case_name)()

    @staticmethod
    def stop_server(args):
        ip, port = args.address.split(':')
        ServerGen.stop_server(ip, int(port))

    @staticmethod
    def run_task(args):
        ip, port = args.address.split(':')
        exec_time_ms = args.exectime
        next_task_ip = None
        next_task_port = None
        taskserver = ServerGen.create(
            Entity.TASK, 'task1', exec_time_ms, next_task_ip, next_task_port)
        taskserver.start(ip, int(port))


def main():
    args_manager = ArgsManager()

    name = 'run_agent'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_agent')
    subargs_manager.address(required=True)

    name = 'run_fileserver'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_fileserver')
    subargs_manager.address(required=True)

    name = 'stop_server'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='stop_server')
    subargs_manager.address(required=True)

    name = 'run_task'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_task')
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
