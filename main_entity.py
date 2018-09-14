from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

from placethings.demo.entity import test_entity
from placethings.demo.entity.base_server import ServerGen, Entity
from placethings.demo.entity.sensor import SensorGen
from placethings.demo.entity.base_client import ClientGen
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

    def next_address(self, required=False):
        self.subparser.add_argument(
            '-ra',
            '--recv_address',
            type=str,
            dest='recv_address',
            default=None,
            required=required,
            help=('receiver address (ip:port). e.g. 10.11.12.13:1234')
        )

    def sensor_type(self, required=False):
        self.subparser.add_argument(
            '-st',
            '--sensor_type',
            type=int,
            dest='sensor_type',
            default=None,
            required=required,
            help=('sensor_type (int)')
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

    def method(self, required=False):
        self.subparser.add_argument(
            '-m',
            '--method',
            type=str,
            dest='method',
            default=None,
            required=required,
            help=('rpc method name')
        )

    def command(self, required=False):
        self.subparser.add_argument(
            '-cmd',
            '--command',
            type=str,
            dest='command',
            default=None,
            required=required,
            help=('command to run')
        )

    def args_list(self, required=False):
        self.subparser.add_argument(
            '-al',
            '--args_list',
            type=str,
            nargs='+',
            dest='args_list',
            default=[],
            required=required,
            help=('args list')
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
    def _split_addr(address):
        ip, port = address.split(':')
        return ip, int(port)

    @classmethod
    def run_agent(cls, args):
        name = args.name
        ip, port = cls._split_addr(args.address)
        update_rootlogger(name, is_log_to_file=True)
        ServerGen.start_server(name, Entity.AGENT, ip, port)

    @classmethod
    def run_fileserver(cls, args):
        name = args.name
        ip, port = cls._split_addr(args.address)
        port = int(port)
        update_rootlogger(name, is_log_to_file=True)
        ServerGen.start_server(name, Entity.FILESERVER, ip, port)

    @classmethod
    def run_task(cls, args):
        name = args.name
        ip, port = cls._split_addr(args.address)
        port = int(port)
        exec_time_ms = args.exectime
        next_ip, next_port = args.recv_address.split(':')
        next_port = int(next_port)
        update_rootlogger(name, is_log_to_file=True)
        ServerGen.start_server(
            name, Entity.TASK, ip, port,
            exec_time_ms, [(next_ip, next_port)])

    @classmethod
    def run_actuator(cls, args):
        name = args.name
        ip, port = cls._split_addr(args.address)
        update_rootlogger(name, is_log_to_file=True)
        ServerGen.start_server(
            name, Entity.TASK, ip, port, 0, None)

    @classmethod
    def run_sensor(cls, args):
        name = args.name
        sensor_type = args.sensor_type
        next_ip, next_port = cls._split_addr(args.recv_address)
        next_port = int(next_port)
        update_rootlogger(name, is_log_to_file=True)
        # def create(cls, name, sensor_type, receiver_dict):
        SensorGen.start_sensor(
            name, sensor_type, [(next_ip, next_port)])

    @classmethod
    def run_client(cls, args):
        name = args.name
        ip, port = cls._split_addr(args.address)
        method = args.method
        command = args.command
        update_rootlogger(name, is_log_to_file=True)
        ClientGen.call_async(ip, port, method, (command))

    @staticmethod
    def run_test(args):
        case_name = args.testcase
        update_rootlogger(case_name, is_log_to_file=True)
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
    subargs_manager.next_address(required=True)

    name = 'run_actuator'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_actuator')
    subargs_manager.name(required=True)
    subargs_manager.address(required=True)

    name = 'run_sensor'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_sensor')
    subargs_manager.name(required=True)
    subargs_manager.address(required=True)
    subargs_manager.sensor_type(required=True)
    subargs_manager.next_address(required=True)

    name = 'run_client'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_client')
    subargs_manager.name(required=True)
    subargs_manager.address(required=True)
    subargs_manager.method(required=True)
    subargs_manager.command(required=True)

    name = 'run_test'
    subargs_manager = args_manager.add_subparser(
        name,
        func=getattr(FuncManager, name),
        help='run_test')
    subargs_manager.testcase(required=True)

    args = args_manager.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
