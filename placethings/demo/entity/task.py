from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time

from placethings.demo.entity.base_client import ClientGen


log = logging.getLogger()


class RPCServer(object):
    def __init__(
            self, name, exec_time_ms, receiver_list=None):
        self.name = name
        self.exec_time_sec = exec_time_ms / 1000.0
        self.receiver_list = receiver_list
        log.info('start Task RPCServer: {}, exectime={}s, receivers={}'.format(
            self.name, self.exec_time_sec, self.receiver_list))

    def _compute(self, data):
        t1 = time.time()
        log.info('(TIME) start computation: {}'.format(t1))
        if self.exec_time_sec > 0:
            time.sleep(self.exec_time_sec)
        t2 = time.time()
        log.info('(TIME) stop computation: {}'.format(t2))
        return 'spent {} to compute result'.format(t2-t1)

    def push(self, data):
        if not self.receiver_list:
            log.info('got data, size={}'.format(len(data)))
            return 'receive data'
        else:
            result = self._compute(data)
            for next_ip, next_port in self.receiver_list:
                log.info('push data to {}:{}'.format(next_ip, next_port))
                ClientGen.call(next_ip, next_port, 'push', result)
            # logging
            log.info('got data: {}'.format(data))
            log.info('compute result: {}'.format(result))
            return result
