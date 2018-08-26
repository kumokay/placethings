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
            Gt (networkx.DiGraph): task graph in a multi-source, single
            destination, no-loop directed graph, where src_k are data sources,
            dst is the actuator, and other nodes in between are tasks

               src1  ────> t11 ────> t12 ... ────  dst
               src2  ────> t21 ────> t22 ... ────┤
                    ...   ...     ...         ...
                    └────> tk1 ────> tk2 ... ────┘

                Gt.node[t] (dict): node, stores information of each task
                Gt[t1][t2] (dict): edge, stores relationship between tasks

                E(t1, t2) (Unit): input/output relationship between t1, t2
                    If t1 will not ouput any data to t2, set the value to 0
                    e.g. Gt[t1][t2][GtInfo.TRAFFIC] = Unit.byte(20)
                        Gt[t1][t2][GtInfo.TRAFFIC] = 0
                _It(t2) (Unit): total input data size to the task. Obtained
                    from sum E(ti, t2) for all ti with an edge to t2. The value
                    will be stored at Gt.node[t][GtInfo.RESOURCE_RQMT]
                _Ot(t1) (Unit): total ouput data size to the task. Obtained
                    from sum E(t1, ti) for all ti with an edge from t1. The
                    value will be stored at Gt.node[t][GtInfo.RESOURCE_RQMT]
                Lt(t,d) (Unit): computation latency of task t runs on device d.
                    Devices can be categorized according to number of CPUs,
                    GPUs, RAM size, and disk space.
                    e.g. Gt.node[t][GtInfo.LATENCY_INFO] = {
                            Device.T2_MICRO: Unit.ms(100),
                            Device.P3_2XLARGE: Unit.ms(5)}
                        device_type = Device.type(Gd.node[d][GdInfo.HARDWARE])
                        Gt.node[t][GtInfo.LATENCY_INFO][device_type] = 100 (ms)
                Rt(t) (dict): minimum resource requirement for task t
                Rt(t,r,d): minimum requirement of resource r for task t of a
                    specific build flavor for that device
                    e.g. build_type = Flavor.type(Device.P3_2XLARGE)
                        assert(build_type == Flavor.GPU)
                        Gt.node[t][GtInfo.RESOURCE_RQMT][build_type] = {
                            Hardware.RAM: Unit.gb(2),
                            Hardware.HD: Unit.mb(512),
                            Hardware.CPU: Unit.percentage(10),
                            Hardware.GPU: Unit.percentage(60),
                            Hardware.CAMERA: 1,
                            Hardware.NIC_INGRESS: Unit.mb(2),  # _It(t)
                            Hardware.NIC_EGRESS: Unit.byte(20),  # _Ot(t)
                        }

            Gd (networkx.DiGraph): a directed graph describes network topology,
                where each node represent a device

                Gd[d] (dict): information of each device, including:

                Ld(d1, d2) (Unit): transmission time between two devices d1, d2
                    If d2 is not reachable from d1, set the value to MAXINT
                    e.g. Gd[d1][d2][GdInfo.LATENCY] = 20 (ms)
                        Gd[d1][d2][GdInfo.LATENCY] = Const.MAXINT
                _Hd(d) (dict): hardware specification of device d.
                    Use this internal information to determine device_type
                    Dd(t) and calculate Rd(d).
                    e.g. Gd.node[d][GdInfo.HARDWARE_SPEC] = {
                        Hardware.RAM: Unit.gb(16),
                        Hardware.HD: Unit.tb(1),
                        Hardware.CPU: 4,
                        Hardware.GPU: 1,
                        Hardware.GPS: 1,
                        Hardware.CAMERA: 1
                        Hardware.NIC_INGRESS: Unit.gbps(10),
                        Hardware.NIC_EGRESS: Unit.gbps(10),
                    }
                _Dd(d) (enum): device type of device d, determined by hardware
                    specification of the device. Used by Gt.node[t] for
                    accessing information of the a certain device type
                    e.g. device_type = Device.type(Gd.node[d][GdInfo.HARDWARE])
                        assert(device_type == Device.T2_MICRO)
                Rd(d) (dict): available resources on device d.
                Rd(d, r) (Unit): availablity of resource r on device d.
                    e.g. Gd.node[d][GdInfo.RESOURCE] = {
                        Hardware.RAM: Unit.gb(12),
                        Hardware.HD: Unit.gb(500),
                        Hardware.CPU: Unit.percentage(80),
                        Hardware.GPU: Unit.percentage(100),
                        Hardware.BW_INGRESS: Unit.mb(100),
                        Hardware.BW_EGRESS: Unit.mb(60),
                        Hardware.GPS: 1,
                        Hardware.PROXIMITY: 1,
                        Hardware.ACCELEROMETER: 1,
                        Hardware.GYROSCOPE: 1,
                        Hardware.CAMERA: 1,
                    }

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

        constrians 1: neighbors in the task graph must also be accessible from
            each other in network graph
            for p in Gt:
                for i in range(1, len(p-1)):
                    X(ti,di) * X(ti+1,di+1) * Ld(di, di+1) < LATENCY_MAX

        constrians 2: device must be able to support what the tasks need
            for d in Gd:
                for r in Rd:
                               len(Gt)
                    Rd(d,r) - { sum ( X(ti,d) * Rt(ti,r,d) ) } >= 0
                                i=1

        """
        pass
