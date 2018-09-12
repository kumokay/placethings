from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from placethings.demo.entity.base_client import BaseClient


class RPCServer(object):

    def __init__(self, name, logger):
        self.name = name
        self.logger = logger

    def _call(self, ip, port, method, *args):
        client = BaseClient(self.name, ip, port, self.logger)
        result = client.call(method, *args)
        return result

    def fetch_from(self, filename, from_ip, from_port):
        result = self._call(from_ip, from_port, 'fetch', filename)
        return 'fetch {} from {}:{}, got: {}'.format(
            filename, from_ip, from_port, result)

    def fetch(self, filename):
        return 'fetch {}'.format(filename)

    def delete(self, filename):
        return 'delete {}'.format(filename)

    def start_prog(self, program_name):
        return 'start_prog {}'.format(program_name)

    def stop_prog(self, program_name):
        return 'stop_prog {}'.format(program_name)
