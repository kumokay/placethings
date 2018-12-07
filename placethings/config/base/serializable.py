from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import os
import importlib

from future.utils import iteritems


class SerializableObject(object):

    _SUPPORTED_MODULES = {
        'placethings.config.base.device_cfg',
        'placethings.config.base.task_cfg'
    }

    def get_classname(self):
        return self.__class__.__name__

    def to_dict(self):
        output = {}
        # put classname here
        output['__classname'] = self.get_classname()
        for objname, obj in iteritems(self.__dict__):
            if isinstance(obj, SerializableObject):
                output[objname] = obj.to_dict()
            else:
                output[objname] = obj
        return output

    def from_dict(self, input_dict):
        for objname, obj in iteritems(input_dict):
            if objname == '__classname':
                assert obj == self.get_classname()
                continue
            if isinstance(obj, dict):
                if '__classname' in obj:
                    classname = obj['__classname']
                    class_def = None
                    for module_name in self._SUPPORTED_MODULES:
                        class_module = importlib.import_module(module_name)
                        class_def = getattr(class_module, classname, None)
                        if class_def:
                            break
                    if class_def:
                        setattr(self, objname, class_def().from_dict(obj))
                    else:
                        assert False
            setattr(self, objname, obj)
        return self

    def to_json(self):
        return json.dumps(
            self, sort_keys=True, indent=4,
            default=lambda obj: obj.to_dict())

    def from_json(self, json_str):
        output_dict = json.loads(json_str)
        return self.from_dict(output_dict)

    def export_to_file(self, filepath):
        filedir = os.path.dirname(filepath)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        assert os.path.exists(filedir)
        with open(filepath, mode='w') as fp:
            fp.write(self.to_json())
        return os.path.exists(filepath)

    def import_from_file(self, filepath):
        with open(filepath, mode='r') as fp:
            json_str = fp.read()
        return self.from_json(json_str)
