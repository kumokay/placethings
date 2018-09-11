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
        log.info('FileServer: {}({})'.format(method, args))

    def fetch(self, filename):
        self._log_method('fetch', filename)
        return 'fetch {}'.format(filename)


class FileServer(object):

    def __init__(self):
        self._server = msgpackrpc.Server(RPCServer())

    def start(self, ip='127.0.0.1', port=18800):
        log.info('start FileServer at {}:{}'.format(ip, port))
        self._server.listen(msgpackrpc.Address(ip, port))
        self._server.start()
