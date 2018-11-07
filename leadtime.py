# python 3.7.0 64-bit

import os

JOBS = 60
PROCESSING_TIME_TABLE = [
    None,
    [None, 2.45, 1.5, 1.95, 2.1],
    [None, 1.55, 0.75, 1.2, 1.05],
    [None, 1.25, 0.5, 0.95, 0.7],
    [None, 1.1, 0.375, 0.825, 0.525]
]
SHOW = True  # for simulation details
INF = 99999
THR = 0.001
FOUR = (1, 2, 3, 4)

# rewrite print
LOGFILE = os.path.join(os.getcwd(), 'log.txt')
with open(LOGFILE, 'w') as f:
    f.truncate()  # clean
buildInPrint = print


def print(*arg, **kw):
    buildInPrint(*arg, **kw)
    with open(LOGFILE, 'a') as f:
        kw.update(dict(file=f))
        buildInPrint(*arg, **kw)


# main procedure
def main():

    for i in FOUR:
        print(f'{i} lots:')
        pt = [x for x in PROCESSING_TIME_TABLE[i]]
        capacity = list()
        pt[2] += pt[4]
        pt = [round(x * i, 3) for x in pt[1: 4]]
        capacity = [round(24 / x * 2, 3) for x in pt]
        print(min(capacity), capacity)
        # print('   ', pt)

    print()
    # input()

    for lots in FOUR:

        print(f'{lots} lots:')
        processing_time = PROCESSING_TIME_TABLE[lots]
        # print(processing_time)
        batch_input = list(range(1, lots + 1))
        stations = [None, 0, 0, 0, 0]
        buffers = [None, list(), list(), list(), list(), list()]  # 5th is output queue
        time_left = [None, INF, INF, INF, INF]
        timer = [0, 0, 0, 0, 0]
        buffers[1] = batch_input

        while len(buffers[5]) < lots:
            someting_happend = True
            while someting_happend:
                someting_happend = False
                # stations to next buffers
                for i in FOUR:
                    if time_left[i] < THR:  # == 0
                        time_left[i] = INF
                        buffers[i + 1].append(stations[i])
                        stations[i] = 0
                        someting_happend = True

                # buffers to stations
                for i in FOUR:
                    if stations[i] == 0 and any(buffers[i]):
                        stations[i] = buffers[i].pop(0)
                        time_left[i] = processing_time[i]
                        someting_happend = True
            if SHOW:
                print(f'{round(timer[0], 3):<7}{stations[1:]}\n\n    {buffers[1:]}\n    {time_left[1:]}\n')

            time_goes = min(time_left[1:])
            if abs(time_goes - INF) < THR:  # == 0
                time_goes = 0
            timer[0] = round(timer[0] + time_goes, 3)
            for i in FOUR:
                if time_left[i] != INF:
                    time_left[i] = round(time_left[i] - time_goes, 3)
                    timer[i] = round(timer[i] + time_goes, 3)

        print(f'{timer[0]} [{timer[1]}, {timer[2] + timer[4]}, {timer[3]}]')
        if SHOW:
            print()
        # input()


if __name__ == '__main__':
    main()
