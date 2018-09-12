from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import msgpackrpc
import time

from placethings.demo.entity.base_client import BaseClient
from placethings.demo.entity.fileserver import RPCServer as FileRPCServer
from placethings.demo.entity.agent import RPCServer as AgentRPCServer
from placethings.demo.entity.task import RPCServer as TaskRPCServer


log = logging.getLogger()


class Entity:
    FILESERVER = 0
    MANAGER = 1
    AGENT = 2
    TASK = 3


class BaseServer(msgpackrpc.Server):
    def __init__(self, name, dispatcher):
        self.name = name
        super(BaseServer, self).__init__(dispatcher)

    def dispatch(self, method, param, responder):
        # get timestamp
        t2 = time.time()
        t1 = param.pop()
        # t1 = param.pop()
        log.info(
            '(TIME) recv: t1={}, t2={}, t_transmit={}'.format(t1, t2, t2-t1))
        log.info('(RECV) {}: {}'.format(method, param))
        # dispatch
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
            super(BaseServer, self).dispatch(method, param, responder)


class ServerGen(object):

    _RPC_CLS = {
        Entity.FILESERVER: FileRPCServer,
        Entity.AGENT: AgentRPCServer,
        Entity.TASK: TaskRPCServer,
    }

    @classmethod
    def start_server(
            cls, name, entity, ip, port, *args):
        args = [name] + list(args)
        rpcobj = cls._RPC_CLS[entity](*args)
        server = BaseServer(name, rpcobj)
        server.listen(msgpackrpc.Address(ip, port))
        server.start()

    @staticmethod
    def stop_server(ip, port):
        client = BaseClient('ServerGen', ip, port)
        result = client.call('STOP')
        log.info('stop server @{}:{}, {}'.format(ip, port, result))
