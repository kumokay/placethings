from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time

from placethings.demo.entity.base_client import BaseClient


class RPCServer(object):
    def __init__(
            self, name, logger, exec_time_ms,
            next_task_ip, next_task_port):
        self.name = name
        self.logger = logger
        self.exec_time_sec = exec_time_ms / 1000.0
        self.next_task_ip = next_task_ip
        self.next_task_port = next_task_port

    @staticmethod
    def _call_async(self, ip, port, method, *args):
        client = BaseClient(self.name, ip, port, self.logger)
        result = client.call_async(method, *args)
        return result

    def compute(self, data):
        time.sleep(self.exec_time_sec)
        return 'spent {} to compute result'.format(self.exec_time_sec)

    def push(self, data, timestamp_dict):
        t1 = time.time()
        # compute data and push to the next task
        result = self.compute(data)
        # dont care about result
        t2 = time.time()
        timestamp_dict[self.name] = (t1, t2)
        if self.next_task_ip and self.next_task_port:
            self._call_async(
                self.next_task_ip, self.next_task_port,
                'push', data, timestamp_dict)
        # logging
        self._log_method('push', data)
        log.info('timestamp_dict: {}'.format(timestamp_dict))
        log.info('got data: {}'.format(data))
        log.info('compute result: {}'.format(result))
        return 'compute data'
