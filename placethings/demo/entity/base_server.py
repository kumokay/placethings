from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import msgpackrpc
import time
import sys

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
    def __init__(self, name, logger, dispatcher):
        self.logger = logger
        self.name = name
        super(BaseServer, self).__init__(dispatcher)

    def dispatch(self, method, param, responder):
        # get timestamp
        t2 = time.time()
        t1 = param.pop()
        # t1 = param.pop()
        self.logger.info(
            '(TIME) recv: t1={}, t2={}, t_transmit={}'.format(t1, t2, t2-t1))
        self.logger.info('(RECV) {}: {}'.format(method, param))
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
    @staticmethod
    def _get_logger(name):
        logpath = '/home/kumokay/github/placethings/log/{}.log'.format(name)
        # cleanup log
        open(logpath, 'w').close()
        logFormatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] {}| %(funcName)s: %(message)s'.format(
                name))
        fileHandler = logging.FileHandler(logpath)
        fileHandler.setFormatter(logFormatter)
        fileHandler.setLevel(logging.DEBUG)
        logger = logging.getLogger(name)
        logger.addHandler(fileHandler)
        return logger

    @staticmethod
    def _get_rpcclass(entity):
        if entity == Entity.FILESERVER:
            rpcclass = FileRPCServer
        elif entity == Entity.AGENT:
            rpcclass = AgentRPCServer
        elif entity == Entity.TASK:
            rpcclass = TaskRPCServer
        else:
            assert False, 'invalid entity: {}'.format(entity)
        return rpcclass

    @classmethod
    def start_server(
            cls, name, entity, ip, port, *args):
        logger = cls._get_logger(name)
        args = [name, logger] + list(args)
        rpcobj = cls._get_rpcclass(entity)(*args)
        server = BaseServer(name, logger, rpcobj)
        server.listen(msgpackrpc.Address(ip, port))
        server.start()

    @staticmethod
    def stop_server(ip, port):
        client = BaseClient('ServerGen', ip, port, logging.getLogger())
        result = client.call('STOP')
        log.info('stop server @{}:{}, {}'.format(ip, port, result))
