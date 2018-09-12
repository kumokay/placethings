from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from placethings.demo.entity.base_client import BaseClient


class RPCServer(object):

    def __init__(self, name):
        self.name = name

    def _call(self, ip, port, method, *args):
        client = BaseClient(self.name, ip, port)
        result = client.call(method, *args)
        return result

    def fetch(self, filename):
        return 'fetch {}'.format(filename)
