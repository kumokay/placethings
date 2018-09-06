from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from aenum import Enum
from future.utils import iteritems
import logging
import json
import os

from placethings.definition import EnumHelper


log = logging.getLogger()

_DEFAULT_FILE_DIR = '/tmp/placethings'


def get_default_file_path(filename):
    return '{}/{}'.format(_DEFAULT_FILE_DIR, filename)


class CustomEncoder(json.JSONEncoder):
    @classmethod
    def _convert_keys_to_strs(cls, dict_obj):
        new_dict = {}
        for key, value in iteritems(dict_obj):
            if isinstance(value, dict):
                value = cls._convert_keys_to_strs(value)
            if EnumHelper.is_enum(key):
                new_dict[EnumHelper.enum_to_str(key)] = value
            else:
                new_dict[key] = value
        return new_dict

    def iterencode(self, obj):
        log.info('encode using CustomEncoder')
        if isinstance(obj, dict):
            obj = self._convert_keys_to_strs(obj)
        return super(CustomEncoder, self).iterencode(obj)


class CustomDecoder(json.JSONDecoder):
    @classmethod
    def _convert_keys_from_strs(cls, dict_obj):
        new_dict = {}
        for key, value in iteritems(dict_obj):
            if isinstance(value, dict):
                value = cls._convert_keys_from_strs(value)
            new_key = EnumHelper.str_to_enum(key)
            if new_key:
                new_dict[new_key] = value
            else:
                new_dict[key] = value
        return new_dict

    def decode(self, obj):
        log.info('encode using CustomDecoder')
        obj = super(CustomDecoder, self).decode(obj)
        if isinstance(obj, dict):
            obj = self._convert_keys_from_strs(obj)
        return obj


def to_json(obj):
    pretty_str = json.dumps(
        obj, indent=4, separators=(',', ': '), cls=CustomEncoder)
    return pretty_str


def from_json(json_str):
    obj = json.loads(json_str, cls=CustomDecoder)
    return obj


def export_to_file(filepath, obj):
    filedir = os.path.dirname(filepath)
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    assert os.path.exists(filedir)
    with open(filepath, mode='w') as fp:
        json.dump(obj, fp, indent=4, separators=(',', ': '), cls=CustomEncoder)
    log.info('exported to file: {}'.format(filepath))
    return os.path.exists(filepath)


def import_from_file(filepath):
    assert os.path.exists(filepath)
    with open(filepath) as fp:
        obj = json.load(fp, cls=CustomDecoder)
    log.info('imported from file: {}'.format(filepath))
    return obj


def export_bundle(filepath, **kwargs):
    bundle = dict(kwargs)
    return export_to_file(filepath, bundle)


def import_bundle(filepath, *args):
    bundle = import_from_file(filepath)
    if not args:
        return bundle
    else:
        obj_list = []
        for name in args:
            obj_list.append(bundle[name])
        return obj_list if obj_list else None
