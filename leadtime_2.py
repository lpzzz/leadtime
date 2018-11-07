# python 3.7.0 64-bit

import os

JOBS = 60
PROCESS_TIME_TABLE = [
    None,
    [None, 2.45, 1.5, 1.95, 2.1],
    [None, 1.55, 0.75, 1.2, 1.05],
    [None, 1.25, 0.5, 0.95, 0.7],
    [None, 1.1, 0.375, 0.825, 0.525]
]
SHOW = True  # for simulation details
INF = 99999
THR = 0.001
PRI = None  # None: FIFO; 2: 2; 4: 4


# rewrite print
LOGFILE = os.path.join(os.getcwd(), 'log_2.txt')
with open(LOGFILE, 'w') as f:
    f.truncate()  # clean
buildInPrint = print
# setting for gantt
ganttfile = os.path.join(os.getcwd(), 'gantt.csv')
with open(ganttfile, 'w') as f:
    f.truncate
    f.write('Station, start_time, finish_time, During, lot, number_of_lot\n')


def print(*arg, **kw):
    buildInPrint(*arg, **kw)
    with open(LOGFILE, 'a') as f:
        kw.update(dict(file=f))
        buildInPrint(*arg, **kw)


# main procedure
def main():

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

    for l in (1, 2, 3, 4):

        print(f'{l} lots:')
        process_time = PROCESS_TIME_TABLE[l]
        # print(process_time)
        lot_input = [1, 2, 3, 4][:l]
        in_process = [None, 1, 1, 1, 1][:l + 1]  # in which process
        stations = [None, 0, 0, 0]
        buffers = [None, list(), list(), list(), None, list()]  # [5]: output
        buffers[4] = buffers[2]  # link buffer 2 & 4

        buffers[1] = lot_input
        time_left = [None, INF, INF, INF]
        timer = [0, 0, 0, 0]

        if SHOW:
            print(f'    {buffers[1:]}\n')

        while len(buffers[5]) < l:
            something_happend = True
            while something_happend:
                something_happend = False
                # stations to next buffers
                for i in (1, 2, 3):
                    if time_left[i] < THR:  # == 0
                        lot = stations[i]
                        stations[i] = 0
                        time_left[i] = INF
                        in_process[lot] += 1  # move to next process
                        buffers[in_process[lot]].append(lot)
                        something_happend = True

                        during = process_time[in_process[lot] - 1]
                        with open(ganttfile, 'a') as f:
                            line = f'{i}, {round(timer[0] - during, 3)}, {timer[0]}, {during}, {lot}, {l}\n'
                            f.write(line)

                # buffers to stations
                for i in (1, 2, 3):
                    if stations[i] == 0 and any(buffers[i]):
                        j = 0
                        if PRI is not None and i == 2:  # station 2 and not FIFO
                            while j < len(buffers[i]) or in_process[buffers[i][j]] != PRI:
                                j + 1  # look for first primary
                            if j == len(buffers[i]):
                                j = 0  # no primary left
                        lot = buffers[i].pop(j)
                        stations[i] = lot
                        time_left[i] = process_time[in_process[lot]]
                        something_happend = True

            if SHOW:
                print(f'{round(timer[0], 3):<7}{stations[1:]}\n\n    {buffers[1:]}\n    {time_left[1:]}\n')

            time_goes = min(time_left[1:])
            if abs(time_goes - INF) < THR:  # == 0
                time_goes = 0
            timer[0] = round(timer[0] + time_goes, 3)
            for i in (1, 2, 3):
                if time_left[i] != INF:
                    time_left[i] = round(time_left[i] - time_goes, 3)
                    timer[i] = round(timer[i] + time_goes, 3)

        print(f'{timer[0]} {timer[1:]}')
        if SHOW:
            print()
        # input()


if __name__ == '__main__':
    main()
