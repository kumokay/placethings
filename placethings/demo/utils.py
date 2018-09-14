from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class AddressManager(object):
    def __init__(self, net):
        self.net = net
        self.address_book = {}

    def get_address_book(self):
        return self.address_book

    def get_task_address(self, task_name, device_name):
        if task_name in self.address_book:
            _, ip, port = self.address_book[task_name]
        else:
            ip = self.net.get_device_ip(device_name)
            port = self.net.get_device_free_port(device_name)
            self.address_book[task_name] = (device_name, ip, port)
        return ip, port
