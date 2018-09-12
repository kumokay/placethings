from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import msgpackrpc
import time


class BaseClient(msgpackrpc.Client):
    def __init__(self, name, ip, port, logger):
        self.name = name
        self.logger = logger
        super(BaseClient, self).__init__(msgpackrpc.Address(ip, port))

    def call(self, method, *args):
        t1 = time.time()
        self.logger.info(
            '(TIME) send: t1={}'.format(t1))
        self.logger.info('(SEND) {}: {}'.format(method, args))
        args = list(args)
        args.append(t1)
        return self.send_request(method, args).get()

    def call_async(self, method, *args):
        t1 = time.time()
        self.logger.info(
            '(TIME) send: t1={}'.format(t1))
        self.logger.info('(SEND) {}: {}'.format(method, args))
        return self.send_request(method, args)
