from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time

from placethings.demo.entity import task as BaseTask


log = logging.getLogger()


class RPCServer(BaseTask.RPCServer):
    def __init__(
            self, name, exec_delay_time_ms, receiver_list=None):
        self.name = name
        self.exec_delay_time_sec = exec_delay_time_ms / 1000.0
        self.receiver_list = receiver_list
        log.info('start task_findObj RPCServer: {}'.format(self.name))
        log.info('exec_delay_time_ms={}s, receivers={}'.format(
            self.exec_delay_time_sec, self.receiver_list))

    def _compute(self, data):
        t1 = time.time()
        log.info('(TIME) start computation: {}'.format(t1))
        log.info('forward data')
        if self.exec_delay_time_sec > 0:
            time.sleep(self.exec_delay_time_sec)
        t2 = time.time()
        log.info('(TIME) stop computation: {}'.format(t2))
        log.info('forward delay: {}'.format(t2-t1))
        return data
