from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from placethings.demo.entity.base_client import ClientGen


log = logging.getLogger()


class RPCServer(object):

    def __init__(self, name):
        self.name = name
        log.info('start Agent RPCServer: {}'.format(self.name))

    def fetch_from(self, filename, from_ip, from_port):
        result = ClientGen.call(from_ip, from_port, 'fetch', filename)
        return 'fetch {} from {}:{}, got: {}'.format(
            filename, from_ip, from_port, result)

    def fetch(self, filename):
        return 'fetch {}'.format(filename)

    def delete(self, filename):
        return 'delete {}'.format(filename)

    def start_prog(self, cmd):
        log.info('try to start prog: {}'.format(cmd))
        return 'start_prog'

    def stop_prog(self, program_name):
        return 'stop_prog {}'.format(program_name)
