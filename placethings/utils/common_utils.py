from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
