from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import msgpackrpc
import time


log = logging.getLogger()


class StoppableServer(msgpackrpc.Server):
    def dispatch(self, method, param, responder):
        method = msgpackrpc.compat.force_str(method)
        if method == 'STOP':
            result = True
            if isinstance(result, msgpackrpc.server.AsyncResult):
                result.set_responder(responder)
            else:
                responder.set_result(result)
            self.stop()
            self.close()
        else:
            super(StoppableServer, self).dispatch(method, param, responder)


class RPCServer(object):

    def __init__(self, name, exec_time_ms, next_task_ip, next_task_port):
        self.name = name
        self.exec_time_sec = exec_time_ms / 1000.0
        self.next_task_ip = next_task_ip
        self.next_task_port = next_task_port

    def _log_method(self, method, *args):
        log.info('Task[{}]: {}({})'.format(self.name, method, args))

    @staticmethod
    def _call_async(ip, port, method, *args):
        client = msgpackrpc.Client(msgpackrpc.Address(ip, port))
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


class Task(object):

    def __init__(
            self, name, exec_time_ms, next_task_ip=None, next_task_port=None):
        self._server = StoppableServer(
            RPCServer(name, exec_time_ms, next_task_ip, next_task_port))

    def start(self, ip='127.0.0.1', port=19000):
        log.info('start Task at {}:{}'.format(ip, port))
        self._server.listen(msgpackrpc.Address(ip, port))
        self._server.start()
