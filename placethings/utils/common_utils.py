from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os


def get_file_path(relative_filepath, parent_dir=None):
    """
    Get file path relatively to parent folder `placethings`
    Args:
        relative_filepath (str): e.g. config_default/task_graph.json
    Returns:
        absolute filepath (str)
    """
    if not parent_dir:
        parent_dir = os.getcwd()  # where main.py is executing
    return '{}/{}'.format(parent_dir, relative_filepath)


def check_file_folder(filepath):
    filedir = os.path.dirname(filepath)
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    assert os.path.exists(filedir)


def get_config_filepath(config_name, config_filename):
    return get_file_path('{}/{}'.format(config_name, config_filename))


def _init_rootlogger(name='', format_str=None, is_log_to_file=False):
    if not format_str:
        format_str = (
            '%(asctime)s {name}|[%(levelname)s] %(funcName)s:'
            ' %(message)s').format(name=name)
    formatter = logging.Formatter(format_str)
    handlers = [
        logging.StreamHandler()
    ]
    if is_log_to_file:
        logpath = get_file_path('log/{}.log'.format(name))
        handlers.append(logging.FileHandler(logpath))
    # set root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    for hdlr in handlers:
        hdlr.setFormatter(formatter)
        hdlr.setLevel(logging.DEBUG)
        logger.addHandler(hdlr)


def update_rootlogger(name='', format_str=None, is_log_to_file=False):
    logger = logging.getLogger()
    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)
    _init_rootlogger(name, format_str, is_log_to_file)
