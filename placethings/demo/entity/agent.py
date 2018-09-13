from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.demo.entity.base_client import BaseClient


log = logging.getLogger()


class RPCServer(object):

    def __init__(self, name):
        self.name = name
        log.info('start RPCServer: {}'.format(self.name))

    def _call(self, ip, port, method, *args):
        client = BaseClient(self.name, ip, port)
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
