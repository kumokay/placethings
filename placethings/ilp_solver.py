from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
# import pulp


log = logging.getLogger()


class Problems:

    @classmethod
    def place_things(cls, target_latency, Gt, Gd):
        """
        Args:
            target_latency (int): latency constrain for this task graph
            Gt (networkx.DiGraph): task graph in the following format, where
                n_src is the data source, n_dst is the actuator, and other
                nodes in between are computaton tasks

               n_src ────> t11 ────> t12 ... ──── n_dst
                    ├────> t21 ────> t22 ... ────┤
                    ...   ...     ...         ...
                    └────> tk1 ────> tk2 ... ────┘

                Gt.node[t] (dict): node, stores information of each task
                Gt[t1][t2] (dict): edge, stores relationship between tasks

                E(t1, t2) (Unit): input/output relationship between t1, t2
                    If t1 will not ouput any data to t2, set the value to 0
                    e.g. Gt[t1][t2][GtInfo.DATA_SZ] = Unit.byte(20)
                        Gt[t1][t2][GtInfo.DATA_SZ] = 0
                It(t2) (Unit): total input data size to the task. Obtained from
                    sum E(t1, t2)
                    e.g. Gt.node[t2][GtInfo.DATA_IN] = Unit.mbs(100)
                Ot(t1) (Unit): total output data size from the task
                    e.g. Gt.node[t1][GtInfo.DATA_OUT] = Unit.mbs(100)
                Lt(t,d) (Unit): computation latency of task t runs on device d.
                    Devices can be categorized according to number of CPUs,
                    GPUs, RAM size, and disk space.
                    e.g. Gt.node[t][GtInfo.LATENCY_INFO] = {
                            Device.T2_MICRO: Unit.ms(100),
                            Device.P3_2XLARGE: Unit.ms(5)}
                        device_type = Device.type(ram, hd, cpu, gpu)
                        Gt.node[t][GtInfo.LATENCY_INFO][device_type] = 100 (ms)
                Rt(t) (dict): minimum resource requirement for task t
                Rt(t,d,r): minimum requirement of resource r for task t of a
                    specific build flavor for that device
                    e.g. build_type = Flavor.type(Device.P3_2XLARGE)
                        e.g. assert(build_type == Flavor.GPU)
                        Gt.node[t][GtInfo.RESOURCE_RQMT][build_type] = {
                            Resource.RAM: Unit.gb(2),
                            Resource.HD: Unit.mb(512),
                            Resource.CPU: 1,
                            Resource.GPU: 1}
                St(t) (dict): sensor requirement for task t
                St(t, s) (int): number of sensors s needed by task t
                    e.g. Gt.node[t][GtInfo.SENSOR_RQMT] = {
                        Sensor.GPS: 1,
                        Sensor.CAMERA: 1}

            Gd (networkx.DiGraph): a directed graph describes network topology,
                where each node represent a device

                Gd[d] (dict): information of each task, including:

                Ld(d1, d2) (Unit): transmission time between two devices d1, d2
                    If d2 is not reachable from d1, set the value to MAXINT
                    e.g. Gd[d1][d2][GdInfo.LATENCY] = 20 (ms)
                        Gd[d1][d2][GdInfo.LATENCY] = Const.MAXINT
                Id(d) (Unit): device input bandwidth
                    e.g. Gd.node[d][GdInfo.BANDWIDTH_IN] = Unit.mbs(100)
                Od(d) (Unit): device output bandwidth
                    e.g. Gd.node[d][GdInfo.BANDWIDTH_OUT] = Unit.mbs(100)
                Hd(d) (dict): hardware specification of device d.
                    Use this information to determine device_type Dd(t).
                    e.g. Gd.node[d][GdInfo.HARDWARE] = {
                        Resource.RAM: Unit.gb(16),
                        Resource.HD: Unit.tb(1),
                        Resource.CPU: 4,
                        Resource.GPU: 1,
                        Sensor.GPS: 1,
                        Sensor.CAMERA: 1}
                Dd(d) (enum): device type of device d, determined by hardware
                    specification of the device.
                    e.g. device_type = Device.type(
                        Gd.node[d][GdInfo.HARDWARE][Resource.RAM],
                        Gd.node[d][GdInfo.HARDWARE][Resource.HW],
                        Gd.node[d][GdInfo.HARDWARE][Resource.CPU],
                        Gd.node[d][GdInfo.HARDWARE][Resource.GPU])
                    assert(device_type == Device.T2MICRO)
                Rd(d) (dict): available computing resources on device d.
                Rd(d, r) (Unit): availablity of resource r on device d.
                    e.g. Gd.node[d][GdInfo.RESOURCE_AVAILABLE] = {
                        Resource.RAM: Unit.gb(12),
                        Resource.HD: Unit.gb(500),
                        Resource.CPU: Unit.percentage(80),
                        Resource.GPU: Unit.percentage(100)}
                Sd(d) (dict): available sensors on device d
                Sd(d, s) (int): number of available sensors s on device d
                    e.g. Gd.node[d][GdInfo.SENSOR_AVAILABLE] = {
                        Sensor.GPS: 1,
                        Sensor.CAMERA: 1}


        decision variable:
            X(t,d) = 1 if assign task t to device d else 0
        objective: minimize longest path's overall latency in the task graph,
            i.e. total execution times + transmission latencies along the path

                             len(p)-1
            minimize   max   {  sum ( X(ti,di) * Lt(ti, di) )
            X(t,d)   p in Gt    i=1
                            len(p)
                        +   sum ( X(ti,di) * X(ti+1,di+1) * Ld(di, di+1) ) }
                            i=1

        constrians: device must be able to support what the task needs
            for d in Gd:
                for t in Gt:
                    X(t,d) * { Id(t) - It(t) } > 0
                    X(t,d) * { Od(t) - Ot(t) } > 0
                    for r in Rt:
                        X(t,d) * { Rd(d,r) - Rt(t,d,r) } > 0
                    for s in St
                        X(t,d) * { Sd(d, s) - St(d, s) > 0


            for
                X(t,d,G)*Id(d1) X(t,d,G)*Io(d2)
        """
        pass
