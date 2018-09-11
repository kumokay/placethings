from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import msgpackrpc
import time

from placethings.demo.entity.fileserver import RPCServer as FileRPCServer
from placethings.demo.entity.agent import RPCServer as AgentRPCServer
from placethings.demo.entity.task import RPCServer as TaskRPCServer


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


class BaseServer():
    def __init__(self, rpcserver_obj, server_name='server'):
        self._server = StoppableServer(rpcserver_obj)
        self._server_name = server_name
        self._ip = None
        self._port = None

    def _call(self, method, *args):
        client = msgpackrpc.Client(msgpackrpc.Address(self.ip, self.port))
        result = client.call(method, *args)
        return result

    def start(self, ip='127.0.0.1', port=18800, device_name=''):
        log.info('start {} @{}({}:{})'.format(
            self._server_name, ip, port, device_name))
        self._addr = (ip, port)
        self._server.listen(msgpackrpc.Address(ip, port))
        self._server.start()

    def stop(self):
        ret = self._call('STOP')
        log.info('stop {}: {}'.format(self._server_name, ret))


class Entity:
    FILESERVER = 0
    MANAGER = 1
    AGENT = 2
    TASK = 3


class ServerGen(object):
    _NEXT_AGENT_ID = 0
    _NEXT_FILESERVER_ID = 0
    _NEXT_TASK_ID = 0

    @classmethod
    def _get_server_info(cls, entity):
        if entity == Entity.FILESERVER:
            name = '{}.{}'.format('fileserver', cls._NEXT_FILESERVER_ID)
            cls._NEXT_FILESERVER_ID += 1
            rpcserver_class = FileRPCServer
        elif entity == Entity.AGENT:
            name = '{}.{}'.format('agent', cls._NEXT_AGENT_ID)
            cls._NEXT_AGENT_ID += 1
            rpcserver_class = AgentRPCServer
        elif entity == Entity.TASK:
            name = '{}.{}'.format('task', cls._NEXT_TASK_ID)
            cls._NEXT_TASK_ID += 1
            rpcserver_class = TaskRPCServer
        else:
            assert False, 'invalid entity: {}'.format(entity)
            return None, None
        return name, rpcserver_class

    @classmethod
    def create(cls, entity_enum, *args):
        name, rpcserver_class = cls._get_server_info(entity_enum)
        rpcserver_obj = rpcserver_class(*args)
        return BaseServer(name, rpcserver_obj)

    @staticmethod
    def stop_server(ip, port):
        client = msgpackrpc.Client(msgpackrpc.Address(ip, port))
        result = client.call('STOP')
        log.info('stop server @{}:{}, {}'.format(ip, port, result))
