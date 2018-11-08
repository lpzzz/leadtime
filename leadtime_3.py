# python 3.7.0 64-bit

import os
# import random

JOBS = 60
PROCESS_TIME_TABLE = [
    None,
    [None, 2.45, 1.5, 1.95, 2.1],
    [None, 1.55, 0.75, 1.2, 1.05],
    [None, 1.25, 0.5, 0.95, 0.7],
    [None, 1.1, 0.375, 0.825, 0.525]
]
SHOW = True  # for simulation details
INF = 9999999
THR = 0.0001
PRI = None  # None: FIFO; 2: 2; 4: 4
N_LOTS = 2
JOBS = 27
WIP_LIMIT = 4
INITIAL_INPUT_INTERVAL = round(24 / 14, 3)  # input interval at beginning

LOGFILE = os.path.join(os.getcwd(), 'log_3.txt')  # logs
with open(LOGFILE, 'w') as f:
    f.truncate()  # clean
buildInPrint = print

GANTTFILE = os.path.join(os.getcwd(), 'gantt_3.csv')  # setting for gantt
with open(GANTTFILE, 'w') as f:
    f.truncate
    f.write('N_of_lot, Station, Start_time, Finish_time, During, lot, is_in_step_4\n')

ORDERFILE = os.path.join(os.getcwd(), 'order_3.csv')  # record for orders
with open(ORDERFILE, 'w') as f:
    f.truncate
    f.write('N_of_order, Start_time, Finish_time, During\n')


def print(*arg, **kw):  # rewrite print
    buildInPrint(*arg, **kw)
    with open(LOGFILE, 'a') as f:
        kw.update(dict(file=f))
        buildInPrint(*arg, **kw)


def main():  # main procedure

    # theoretical capacity
    for l in (1, 2, 3, 4):  # l: number of lots
        print(f'{l} lots:')
        pt = [x for x in PROCESS_TIME_TABLE[l]]
        capacity = list()
        pt[2] += pt[4]
        pt = [round(x * l, 3) for x in pt[1: 4]]
        capacity = [round(24 / x * 2, 3) for x in pt]
        print(min(capacity), capacity)
        # print('   ', pt)

    print()
    # input()

    for l in [N_LOTS]:

        print(f'{l} lots:')
        process_time = PROCESS_TIME_TABLE[l]
        # print(process_time)

        stations = [None, [0, 0], [0, 0], [0, 0]]
        buffers = [None, list(), list(), list(), None, list()]  # [5]: output
        buffers[4] = buffers[2]  # link buffer 2 & 4

        lots_left = [i + 1 for i in range(JOBS * l)]
        in_process = [None] + [1] * (JOBS * l)  # [lot] in which process
        iii = 0  # initial input interval
        initiated = False
        wip = 0
        previous_wip = WIP_LIMIT
        job_code = 0
        order = list()
        time_left = [None, [INF, INF], [INF, INF], [INF, INF]]
        timer = [0, [0, 0], [0, 0], [0, 0]]
        if SHOW:
            print(f'    {buffers[1:]}\n')

        while len(buffers[5]) < JOBS * l:
            print(wip)
            if iii < THR:  # == 0
                if previous_wip > 0:
                    order.append([timer[0]])
                    iii = INITIAL_INPUT_INTERVAL
                    buffers[1] += lots_left[:l]
                    lots_left = lots_left[l:]
                    wip += 1
                    previous_wip -= 1
                else:
                    initiated = True

            something_happend = True
            while something_happend:
                something_happend = False

                for i in (1, 2, 3):  # stations to next buffers
                    for machine in (0, 1):
                        if time_left[i][machine] < THR:  # == 0
                            lot = stations[i][machine]
                            stations[i][machine] = 0
                            time_left[i][machine] = INF
                            p = in_process[lot]
                            in_process[lot] += 1  # move to next process
                            buffers[in_process[lot]].append(lot)
                            something_happend = True

                            during = process_time[p]
                            with open(GANTTFILE, 'a') as f:
                                line = f'{l}, {i}-{machine}, {round(timer[0] - during, 3)}, {timer[0]}, {during}, {lot % (l * WIP_LIMIT)}, {p == 4}\n'
                                f.write(line)

                while len(buffers[5]) // l > job_code:  # output
                    job_code += 1
                    something_happend = True
                    wip -= 1
                    if any(order):
                        # print(order)
                        j = len(order) - 1
                        try:
                            while len(order[j]) == 1:  # only record start time
                                j -= 1
                            j += 1  # last one with only start time
                        except IndexError:
                            j = 0
                        order[j] += [timer[0], round(timer[0] - order[j][0], 3)]  # record finish time and during
                        with open(ORDERFILE, 'a') as f:
                            line = f'{j + 1}, {order[j][0]}, {order[j][1]}, {order[j][2]}\n'
                            f.write(line)

                if initiated:  # input
                    while any(lots_left) and wip + previous_wip < WIP_LIMIT:
                        order.append([timer[0]])  # record start time
                        buffers[1] += lots_left[:l]
                        lots_left = lots_left[l:]
                        wip += 1
                        something_happend = True

                for i in (1, 2, 3):  # buffers to stations
                    if any(buffers[i]):
                        try:
                            # idle = random.choice([machine for machine in (0, 1) if stations[i][machine] == 0])  # choose randomly
                            idle = [machine for machine in (0, 1) if stations[i][machine] == 0][0]  # choose the first idle machine
                            j = 0
                            if PRI is not None and i == 2:  # not FIFO and station 2
                                try:
                                    while in_process[buffers[i][j]] != PRI:
                                        j += 1  # look for first primary
                                        # print(j)
                                    print('!!!!!', j)
                                except IndexError:
                                    j = 0

                            lot = buffers[i].pop(j)
                            stations[i][idle] = lot
                            time_left[i][idle] = process_time[in_process[lot]]
                            something_happend = True

                        except IndexError:
                            pass  # no machine idle

            if SHOW:
                print(f'{round(timer[0], 3):<7}{stations[1:]}\n\n    {buffers[1:]}\n    {time_left[1:] + [iii]}\n')

            time_goes = min([min(t_pair) for t_pair in time_left[1:]])
            if not initiated:
                time_goes = min(time_goes, iii)
            if abs(time_goes - INF) < THR:  # == 0
                time_goes = 0
            timer[0] = round(timer[0] + time_goes, 3)
            if not initiated:  # != 0
                iii = round(iii - time_goes, 3)
            for i in (1, 2, 3):
                for machine in (0, 1):
                    if abs(time_left[i][machine] - INF) > THR:  # != 0
                        time_left[i][machine] = round(time_left[i][machine] - time_goes, 3)
                        timer[i][machine] = round(timer[i][machine] + time_goes, 3)

        print(f'{timer[0]} {timer[1:]}')
        if SHOW:
            print()
        # input()


if __name__ == '__main__':
    main()
