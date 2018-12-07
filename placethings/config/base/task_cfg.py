from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy

from future.utils import iteritems
import networkx as nx

from placethings.config.base.device_cfg import (
    ComputationLibrary, ComputationResource)
from placethings.config.base.serializable import SerializableObject
from placethings.config.base.utils import size_str_to_bits, time_str_to_ms


class Build(SerializableObject):
    def __init__(
            self, exec_cmd='', latency='0ms', computation_resource=None,
            computation_library=None):
        if not computation_resource:
            computation_resource = ComputationResource()
        if not computation_library:
            computation_library = ComputationLibrary()
        assert type(exec_cmd) == unicode
        assert type(latency) == unicode
        assert type(computation_resource) == ComputationResource
        assert type(computation_library) == ComputationLibrary
        assert time_str_to_ms(latency) >= 0
        self.exec_cmd = exec_cmd
        self.latency = latency
        self.computation_resource = ComputationResource()
        self.computation_library = ComputationLibrary()


class Task(SerializableObject):
    def __init__(self, build_dict=None):
        if not build_dict:
            build_dict = {}
        assert type(build_dict) == dict
        self.items = {}  # {build_flavor: build_obj}
        for build_name, build_obj in iteritems(build_dict):
            self.add_build(build_name, build_obj)

    def add_build(self, build_name, build_obj):
        assert type(build_name) == unicode
        assert type(build_obj) == Build
        self.items[build_name] = build_obj

    def has_build(self, build_name):
        assert type(build_name) == unicode
        return build_name in self.items

    def get_build(self, build_name):
        assert type(build_name) == unicode
        return self.items[build_name]


class TaskSpec(SerializableObject):
    def __init__(self, task_dict=None):
        if not task_dict:
            task_dict = {}
        assert type(task_dict) == dict
        self.items = {}  # {build_flavor: build_obj}
        for task_name, task_obj in iteritems(task_dict):
            self.add_task(task_name, task_obj)

    def add_task(self, task_name, task_obj):
        assert type(task_name) == unicode
        assert type(task_obj) == Task
        self.items[task_name] = task_obj

    def has_task(self, task_name):
        assert type(task_name) == unicode
        return task_name in self.items

    def get_task(self, task_name):
        assert type(task_name) == unicode
        return self.items[task_name]


class TaskLink(SerializableObject):
    def __init__(self, data_traffic='0b'):
        assert type(data_traffic) == unicode
        assert size_str_to_bits(data_traffic) >= 0
        self.data_traffic = data_traffic


class TaskData(SerializableObject):
    def __init__(self, task_spec=None, task_dict=None, link_dict=None):
        if not task_spec:
            task_spec = TaskSpec()
        if not task_dict:
            task_dict = {}
        if not link_dict:
            link_dict = {}
        assert type(task_spec) == TaskSpec
        assert type(task_dict) == dict
        assert type(link_dict) == dict
        for task_id, task_name in iteritems(task_dict):
            assert type(task_id) == unicode
            assert type(task_name) == unicode
            assert task_spec.has_task(task_name)
        for src_task_id, dst_task_dict in iteritems(link_dict):
            assert src_task_id in task_dict
            for dst_task_id, task_link in iteritems(dst_task_dict):
                assert dst_task_id in task_dict
                assert type(task_link) == TaskLink
        self.task_spec = task_spec
        self.task_dict = task_dict  # {task_name: task_obj}
        self.link_dict = link_dict
        # {src_device: {
        #     dst_device1: link_attr,
        #     dst_device2: link_attr}}

    def to_graph(self, is_export=False):
        base_graph = nx.DiGraph()
        for task_name, task_obj in iteritems(self.task_dict):
            base_graph.add_node(task_name)
        for src_task, dst_task_dict in iteritems(self.link_dict):
            for dst_task in dst_task_dict:
                assert src_task in base_graph.nodes()
                assert dst_task in base_graph.nodes()
                base_graph.add_edge(src_task, dst_task)
        return base_graph

    def has_task(self, task_id):
        return task_id in self.task_dict

    def get_task_dict(self):
        return self.task_dict

    def add_task(self, task_id, task_name):
        assert type(task_id) == unicode
        assert type(task_name) == unicode
        assert self.task_spec.has_task(task_name)
        assert task_id not in self.task_dict
        task_obj = self.task_spec.get_task(task_name)
        self.task_dict[task_id] = copy.deepcopy(task_obj)

    def add_link(self, src_task_id, dst_task_id, task_link):
        assert src_task_id in self.task_dict
        assert dst_task_id in self.task_dict
        assert type(task_link) == TaskLink
        src_task_obj = self.task_dict[src_task_id]
        dst_task_obj = self.task_dict[dst_task_id]
        assert type(src_task_obj) == Task
        assert type(dst_task_obj) == Task
        if src_task_id not in self.link_dict:
            self.link_dict[src_task_id] = {}
        assert dst_task_id not in self.link_dict[src_task_id]
        self.link_dict[src_task_id][dst_task_id] = (
            copy.deepcopy(task_link))
