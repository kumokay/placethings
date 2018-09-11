from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import msgpackrpc


log = logging.getLogger()


class RPCServer(object):

    @staticmethod
    def _log_method(method, *args):
        log.info('Agent: {}({})'.format(method, args))

    @staticmethod
    def _call(ip, port, method, *args):
        client = msgpackrpc.Client(msgpackrpc.Address(ip, port))
        result = client.call(method, *args)
        return result

    def fetch_from(self, filename, from_ip, from_port):
        self._log_method('fetch_from', filename, from_ip, from_port)
        result = self._call(from_ip, from_port, 'fetch', filename)
        return 'fetch {} from {}:{}, got: {}'.format(
            filename, from_ip, from_port, result)

    def fetch(self, filename):
        self._log_method('fetch', filename)
        return 'fetch {}'.format(filename)

    def delete(self, filename):
        self._log_method('delete', filename)
        return 'delete {}'.format(filename)

    def start_prog(self, program_name):
        self._log_method('start_prog', program_name)
        return 'start_prog {}'.format(program_name)

    def stop_prog(self, program_name):
        self._log_method('stop_prog', program_name)
        return 'stop_prog {}'.format(program_name)


class Agent(object):

    def __init__(self):
        self._server = msgpackrpc.Server(RPCServer())

    def start(self, ip='127.0.0.1', port=18900):
        log.info('start Agent at {}:{}'.format(ip, port))
        self._server.listen(msgpackrpc.Address(ip, port))
        self._server.start()
