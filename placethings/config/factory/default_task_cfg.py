from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from placethings.config.base import device_cfg, task_cfg

"""
task graph

  capture_image -> detect_object -> send_notification
"""


def create_default_task_spec():
    task_spec = task_cfg.TaskSpec()

    # task_camera

    task = task_cfg.Task()
    comp_resource = device_cfg.ComputationResource(
        cpu_utilization='10%', gpu_utilization='0%', disk_space='10MB',
        ram_size='1GB')
    exec_cmd = (
        "cd {progdir} && python main_entity.py run_task -n task_camera "
        "-en task_forward -a {docker_addr} -ra {next_addr} &> /dev/null &")
    latency = '1ms'
    build = task_cfg.Build(
        exec_cmd=exec_cmd, latency=latency, computation_resource=comp_resource)
    task.add_build('default', build)
    task_spec.add_task('task_camera', task)

    # task_findObj

    task = task_cfg.Task()
    comp_resource = device_cfg.ComputationResource(
        cpu_utilization='80%', gpu_utilization='0%', disk_space='200MB',
        ram_size='1GB')
    exec_cmd = (
        "cd {progdir} && python main_entity.py run_task -n task_findObj "
        "-en task_findObj -a {self_addr} -ra {next_addr} "
        "-al local &> /dev/null &")
    latency = '2400ms'
    build = task_cfg.Build(
        exec_cmd=exec_cmd, latency=latency, computation_resource=comp_resource)
    task.add_build('default', build)

    comp_resource = device_cfg.ComputationResource(
        cpu_utilization='60%', gpu_utilization='0%', disk_space='200MB',
        ram_size='4GB')
    exec_cmd = (
        "cd {progdir} && python main_entity.py run_task -n task_findObj "
        "-en task_findObj -a {self_addr} -ra {next_addr} "
        "-al local &> /dev/null &")
    latency = '1600ms'
    build = task_cfg.Build(
        exec_cmd=exec_cmd, latency=latency, computation_resource=comp_resource)
    task.add_build('t3.large', build)  # build_name equals to device name now

    comp_resource = device_cfg.ComputationResource(
        cpu_utilization='10%', gpu_utilization='60%', disk_space='2GB',
        ram_size='8GB')
    exec_cmd = (
        "cd {progdir} && python main_entity.py run_task -n task_findObj "
        "-en task_findObj -a {self_addr} -ra {next_addr} "
        "-al offload 172.17.49.60:18800 &> /dev/null &")
    latency = '860ms'
    build = task_cfg.Build(
        exec_cmd=exec_cmd, latency=latency, computation_resource=comp_resource)
    task.add_build('p3.2xlarge', build)  # build_name equals to device name now

    task_spec.add_task('task_findObj', task)

    # task_alert

    task = task_cfg.Task()
    comp_resource = device_cfg.ComputationResource(
        cpu_utilization='10%', gpu_utilization='0%', disk_space='10MB',
        ram_size='1GB')
    exec_cmd = (
        "cd {progdir} && python main_entity.py run_task -n task_alert "
        "-en task_forward -a {self_addr} -ra 172.17.51.1:18900 &> /dev/null &")
    latency = '1ms'
    build = task_cfg.Build(
        exec_cmd=exec_cmd, latency=latency, computation_resource=comp_resource)
    task.add_build('default', build)
    task_spec.add_task('task_alert', task)

    return task_spec


def create_default_task_data():
    task_spec = create_default_task_spec()
    task_data = task_cfg.TaskData(task_spec=task_spec)
    task_data.add_task('capture_image', 'task_camera')
    task_data.add_task('detect_object', 'task_findObj')
    task_data.add_task('send_notification', 'task_alert')

    task_link = task_cfg.TaskLink(data_traffic='2MB')
    task_data.add_link('capture_image', 'detect_object', task_link)

    task_link = task_cfg.TaskLink(data_traffic='20B')
    task_data.add_link('detect_object', 'send_notification', task_link)

    return task_data
