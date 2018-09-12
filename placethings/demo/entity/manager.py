from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import iteritems
import logging

from placethings.demo.entity.base_client import BaseClient


log = logging.getLogger()


class Manager(object):

    def __init__(
            self, name, fileserver_ip, fileserver_port,
            task_data, device_data):
        self.name = name
        self.fileserver_ip = fileserver_ip
        self.fileserver_port = fileserver_port
        self.task_data = task_data
        self.device_data = device_data
        self.cur_map = None
        self.cur_device_addr = None
        self.cur_deploy_cnt = 0

    def call(self, ip, port, method, *args):
        client = BaseClient(self.name, ip, port, logging.getLogger())
        result = client.call(method, *args)
        return result

    def clean_up(self, servermap):
        for ip, port in iteritems(servermap):
            result = self.call(ip, port, 'STOP')
            log.info('stop server @{}:{}, {}'.format(ip, port, result))

    def init_deploy(self, mapping, device_addr):
        log.info('deploy {} ===='.format(self.cur_deploy_cnt))
        for task, device in iteritems(mapping):
            ip, port = device_addr[device]
            result = self.call(
                ip, port, 'fetch_from', task,
                self.fileserver_ip, self.fileserver_port)
            log.info('depoly {} to {}: {}'.format(task, device, result))
        self.cur_map = mapping
        self.cur_deploy_cnt += 1

    def re_deploy(self, mapping, device_addr):
        log.info('deploy {} ===='.format(self.cur_deploy_cnt))
        for task, device in iteritems(mapping):
            device_has_task = self.cur_map[task]
            if device_has_task == device:
                continue
            ip, port = device_addr[device]
            server_ip, server_port = device_addr[device_has_task]
            result = self.call(
                ip, port, 'fetch_from', task, server_ip, server_port)
            log.info('move {} from {} to {}: {}'.format(
                task, device_has_task, device, result))
        self.cur_map = mapping
        self.cur_deploy_cnt += 1
