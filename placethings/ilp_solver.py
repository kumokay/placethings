from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import range
from collections import defaultdict
from future.utils import listvalues
import logging
from itertools import izip as zip
import pulp
import networkx as nx

from placethings.definition import Const, GdInfo, GtInfo, Hardware
from placethings.task_graph import TaskGraph


log = logging.getLogger()


def place_things(target_latency, Gt, Gd, src_map, dst_map):
    """
    Args:
        target_latency (int): latency constrain for this task graph
        source_list (list): source nodes in the task graph
        dst_list (list): destination nodes in the task graph
        Gt (networkx.DiGraph): task graph in a multi-source, single
        destination, no-loop directed graph, where src_k are data sources,
        dst is the actuator, and other nodes in between are tasks

           src1 -----> t11 -----> t12 ... ----->  dst
           src2 -----> t21 -----> t22 ... ----->
                 ...   ...  ...  ...
                -----> tk1 -----> tk2 ... ----->

            Gt.node[t] (dict): node, stores information of each task
            Gt[t1][t2] (dict): edge, stores relationship between tasks

            E(t1, t2) (Unit): input/output relationship between t1, t2
                If t1 will not ouput any data to t2, set the value to 0
                e.g. Gt[t1][t2][GtInfo.TRAFFIC] = Unit.byte(20)
                    Gt[t1][t2][GtInfo.TRAFFIC] = 0
            _It(t2) (Unit): total input data size to the task. Obtained
                from sum E(ti, t2) for all ti with an edge to t2. The value
                will be stored at Gt.node[t][GtInfo.RESRC_RQMT]
            _Ot(t1) (Unit): total ouput data size to the task. Obtained
                from sum E(t1, ti) for all ti with an edge from t1. The
                value will be stored at Gt.node[t][GtInfo.RESRC_RQMT]
            Lt(t,d) (Unit): computation latency of task t runs on device d.
                Devices can be categorized according to number of CPUs,
                GPUs, RAM size, and disk space.
                e.g. Gt.node[t][GtInfo.LATENCY_INFO] = {
                        Device.T2_MICRO: Unit.ms(100),
                        Device.P3_2XLARGE: Unit.ms(5)}
                    device_type = Device.type(Gd.node[d][GdInfo.HARDWARE])
                    Gt.node[t][GtInfo.LATENCY_INFO][device_type] = 100 (ms)
            Rt(t) (dict): minimum RESRC requirement for task t
            Rt(t,r,d): minimum requirement of RESRC r for task t of a
                specific build flavor for that device
                e.g. build_type = Flavor.type(Device.P3_2XLARGE)
                    assert(build_type == Flavor.GPU)
                    Gt.node[t][GtInfo.RESRC_RQMT][build_type] = {
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
                e.g. Gd.node[d][GdInfo.HARDWARE] = {
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
            Rd(d) (dict): available RESRCs on device d.
            Rd(d, r) (Unit): availablity of RESRC r on device d.
                e.g. Gd.node[d][GdInfo.RESRC] = {
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

                         len(p)
        minimize   max   {  sum ( X(ti,di) * Lt(ti, di) )
        X(t,d)   p in Gt    i=1
                       len(p)-1
                    +   sum ( X(ti,di) * X(ti+1,di+1) * Ld(di, di+1) ) }
                        i=1

        this can be simplified by an auxiliary variable and rewrote as:

            minimize Y , where Y = max {....} above

        with additional constrains:

        for p in Gt:
                      len(p)
                Y >=   max   {  sum ( X(ti,di) * Lt(ti, di) )
                     p in Gt    i=1
                      len(p)-1
                   +   sum ( X(ti,di) * X(ti+1,di+1) * Ld(di, di+1) ) }
                       i=1

    constrians 1: neighbors in the task graph must also be accessible from
        each other in network graph
        for (ti, tj) in Gt.edges():
            for all combinations (di, dj) in Gd:
                X(ti,di) * X(tj,dj) * Ld(di, dj) < LATENCY_MAX

    constrians 2: device must be able to support what the tasks need
        for d in Gd:
            for r in Rd:
                           len(Gt)
                Rd(d,r) - { sum ( X(ti,d) * Rt(ti,r,d) ) } >= 0
                            i=1

    constrains 3: task -> device is one-to-one mapping, and all task must be
        mapped to one device

    since linear programming cannot have variable multiplication,
    use a helper variable XX to replace X(ti,di) * X(tj,dj)

        X(ti,di) * X(tj,dj) ---replace---> XX(X(ti,di),X(tj,dj))

    with additional constrains
        XX(X(ti,di),X(tj,dj)) + 1 >= X(ti,di) + X(tj,dj)
        XX(X(ti,di),X(tj,dj)) * 2 <= X(ti,di) + X(tj,dj)

    """
    # define invalid_latency as a constrain to filter out meaningless
    # solutions
    invalid_latency = target_latency * 2
    log.info((
        'set invalid_latency={latency}. skip neighbors cannot be reached '
        'within {latency} ms.').format(
            latency=invalid_latency))

    # Generate all possible mappings of device_i <-> task_i
    mapped_tasks = list(src_map) + list(dst_map)
    mapped_devices = listvalues(src_map) + listvalues(dst_map)
    tasks = [t for t in Gt.nodes() if t not in mapped_tasks]
    devices = [d for d in Gd.nodes() if d not in mapped_devices]
    log.info('find possible mappings for {} tasks in {} devices'.format(
        len(tasks), len(devices)))

    # create LP problem
    prob = pulp.LpProblem("placethings", pulp.LpMinimize)
    # auxiliary variable: it represent the longest path's overall latency
    # in the task graph
    Y = pulp.LpVariable(
        'LongestPathLength',
        lowBound=0,
        upBound=Const.INT_MAX,
        cat='Interger')
    # objective: minimize longest path's overall latency in the task graph
    # later, add additional constrains for the auxiliary variable
    prob += Y

    # decision variable: X(t,d) = 1 if assign task t to device d else 0
    X = defaultdict(dict)
    all_unknown_X = []
    for t in Gt.nodes():
        for d in Gd.nodes():
            X[t][d] = None  # init invalid value
    for t in mapped_tasks:
        for d in Gd.nodes():
            X[t][d] = 0
    for d in mapped_devices:
        for t in Gt.nodes():
            X[t][d] = 0
    for t in mapped_tasks:
        d_known = Gt.node[t][GtInfo.DEVICE]
        X[t][d_known] = 1
    for t in tasks:
        for d in devices:
            if X[t][d] is None:
                X[t][d] = pulp.LpVariable(
                    'X_{}_{}'.format(t, d),
                    lowBound=0,
                    upBound=1,
                    cat='Integer')
                all_unknown_X.append(X[t][d])
        # 1-1 map
        prob += pulp.lpSum(listvalues(X[t])) == 1
    # number of X == 1 must equal to number of tasks
    log.info('there are {} unknowns'.format(len(all_unknown_X)))
    assert len(all_unknown_X) == len(tasks) * len(devices)
    prob += pulp.lpSum(all_unknown_X) == len(tasks)
    # auxiliary variable: use XX to replace X[ti][di] * X[tj][dj]
    XX = defaultdict(dict)
    all_XX = []
    for ti in Gt.nodes():
        for di in Gd.nodes():
            for tj in Gt.nodes():
                for dj in Gd.nodes():
                    if ti == tj or di == dj:
                        XX[(ti, di)][(tj, dj)] = 0
                    elif (ti, tj) not in Gt.edges():
                        XX[(ti, di)][(tj, dj)] = 0
                    elif Gd[di][dj][GdInfo.LATENCY] > invalid_latency:
                        # constrians 1: neighbors in the task graph must also
                        # be accessible from each other in the network graph
                        XX[(ti, di)][(tj, dj)] = 0
                    else:
                        XX[(ti, di)][(tj, dj)] = pulp.LpVariable(
                            'XX_{}_{}'.format((ti, di), (tj, dj)),
                            lowBound=0,
                            upBound=1,
                            cat='Integer')
                        all_XX.append(XX[(ti, di)][(tj, dj)])
                        # add constrains
                        prob += (
                            XX[(ti, di)][(tj, dj)] + 1
                            >= X[ti][di] + X[tj][dj])
                        prob += (
                            XX[(ti, di)][(tj, dj)] * 2
                            <= X[ti][di] + X[tj][dj])
    log.info('there are {} combinations for links'.format(len(all_XX)))
    prob += pulp.lpSum(all_XX) == len(Gt.edges())

    # Generate all simple paths in the graph G from source to target.
    all_paths = []
    for src in src_map:
        for dst in dst_map:
            paths = list(nx.all_simple_paths(Gt, src, dst))
            all_paths += paths
    all_mappings = pulp.combination(devices, len(tasks))
    task_to_idx = dict(zip(tasks, range(len(tasks))))
    # use constrains to model Y, the longest path for each mapping
    for device_mapping in all_mappings:
        for path in all_paths:
            assert path[0] in src_map
            assert path[len(path)-1] in dst_map
            path_vars = []
            # first node: src
            ti = path[0]
            di = Gt.node[ti][GtInfo.DEVICE]
            # device_mapping start from path[1] to path[N-1]
            for j in range(1, len(path)-1):
                tj = path[j]
                dj = device_mapping[task_to_idx[tj]]
                assert Gt.node[tj][GtInfo.DEVICE] == (
                    TaskGraph.DEVICE_NOT_ASSIGNED)
                assert dj in Gd.nodes()
                # get transmission latency from di -> dj
                Ld_di_dj = Gd[di][dj][GdInfo.LATENCY]
                # path_vars.append((X[ti][di] * X[tj][dj]) * Ld_di_dj)
                path_vars.append(XX[(ti, di)][(tj, dj)] * Ld_di_dj)
                # get computation latency for task tj at dj
                dj_type = Gd.node[dj][GdInfo.DEVICE_TYPE]
                # get latency of the default build flavor
                Lt_tj_dj = listvalues(
                    Gt.node[tj][GtInfo.LATENCY_INFO][dj_type])[0]
                path_vars.append(X[tj][dj] * Lt_tj_dj)
                ti = tj
                di = dj
            # last node: dst
            tj = path[len(path)-1]
            dj = Gt.node[tj][GtInfo.DEVICE]
            Ld_di_dj = Gd[di][dj][GdInfo.LATENCY]
            # path_vars.append(X[ti][di] * X[tj][dj] * Ld_di_dj)
            path_vars.append(XX[(ti, di)][(tj, dj)] * Ld_di_dj)
            # add constrain
            prob += Y >= pulp.lpSum(path_vars)

    # constrians 2: device must be able to support what the tasks need
    #     for d in Gd:
    #         for r in Rd:
    #                        len(Gt)
    #             Rd(d,r) - { sum ( X(ti,d) * Rt(ti,r,d) ) } >= 0
    #                         i=1
    for di in devices:
        for resrc in Hardware:
            # get available RESRC or set to 0
            Rd_d_r = Gd.node[di][GdInfo.RESRC].get(resrc, 0)
            var_list = []
            for ti in tasks:
                di_type = Gd.node[di][GdInfo.DEVICE_TYPE]
                # get the default flavor
                ti_flavor = list(
                    Gt.node[ti][GtInfo.LATENCY_INFO][di_type])[0]
                Rt_t_r_d = (
                    Gt.node[ti][GtInfo.RESRC_RQMT][ti_flavor].get(
                        resrc, 0))
                var_list.append(X[t][d] * Rt_t_r_d)
            prob += Rd_d_r - pulp.lpSum(var_list) >= 0

    # solve
    status = prob.solve()
    log.info('status={}'.format(pulp.LpStatus[status]))
    for t in Gt.nodes():
        for d in Gd.nodes():
            if pulp.value(X[t][d]):
                log.info('map: {} <-> {}, X_t_d={}'.format(
                    t, d, pulp.value(X[t][d])))
