import logging
import matplotlib.pyplot as plt
import csv
import numpy as np

import datetime

import matplotlib.pyplot as plt
from matplotlib.dates import (YEARLY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)

import numpy


# number of bytes to read at the end of the csv. if None, read all
_CSV_READ_SIZE = 1024 * 8 * 8 * 8 * 3
_CSV_READ_SIZE = None

# plot size settings
_PLOT_WIDTH = 1600
_PLOT_HEIGHT = 900
_PLOT_DPI = 96


def average_timedelta(input_list):
    if len(input_list) == 0:
        return 0
    return (sum(input_list, datetime.timedelta(0))) / len(input_list)


def average(input_list):
    if len(input_list) == 0:
        return 0
    return (1.0 * sum(input_list)) / len(input_list)


def convert_to_moving_average(date_value_tuple, window_size=5):
    results = []
    recent_values = []
    for date, value in date_value_tuple:
        recent_values.append(value)
        recent_values = recent_values[-window_size:]
        results.append((date, average(recent_values)))
    return results


def convert_to_max_of_last_n(date_value_tuple, window_size=5):
    results = []
    recent_values = []
    for date, value in date_value_tuple:
        recent_values.append(value)
        recent_values = recent_values[-window_size:]
        results.append((date, max(recent_values)))
    return results


def datetime_from_date_and_time_string(date_str, time_str):
    year, month, day = date_str.split('-')
    hour, minute, second = time_str.split(':')
    return datetime.datetime(year=int(year),
                             month=int(month),
                             day=int(day),
                             hour=int(hour),
                             minute=int(minute),
                             second=int(second))


def remove_duplicate_data_points(date_value_tuple):
    results = []
    for idx in range(len(date_value_tuple)):
        if idx == 0:
            results.append(date_value_tuple[idx])
            continue

        try:
            if (date_value_tuple[idx - 1][1]
                    == date_value_tuple[idx][1]
                    == date_value_tuple[idx + 1][1]):
                continue
            else:
                results.append(date_value_tuple[idx])
        except IndexError:
            # if there is an error in lookup (probably at the beginning or end
            # of the list) then just include the value
            results.append(date_value_tuple[idx])
    return results


def print_dropout_stats(connected_states):
    total_duration = connected_states[-1][0] - connected_states[0][0]
    dropouts = 0
    dropout_durations = []
    idx = 0
    for idx, (date, state) in enumerate(connected_states):
        if state == 0:
            dropouts += 1
            try:
                dropout_duration = connected_states[idx+1][0] - connected_states[idx][0]
            except IndexError:
                pass
            else:
                dropout_durations.append(dropout_duration)
    dropout_durations.sort()
    durations_5_perc = int(len(dropout_durations) * 10.0 / 100.0)
    try:
        logging.info(f"in the last {total_duration}, {dropouts} dropouts")
        logging.info(f"max:       {max(dropout_durations)}")
        logging.info(f"worst 10%: {average_timedelta(dropout_durations[-durations_5_perc:])}")
        logging.info(f"average:   {average_timedelta(dropout_durations)}")
        logging.info(f"best 10%:  {average_timedelta(dropout_durations[:durations_5_perc])}")
    except ValueError:
        # no dropouts
        pass


def save_data_over_time_graph(connected_states, latencies, down_speeds, up_speeds):
    fix, ax = plt.subplots()
    plt.figure(figsize=(_PLOT_WIDTH/_PLOT_DPI, _PLOT_HEIGHT/_PLOT_DPI), dpi=_PLOT_DPI)

    logging.info('plot connected_states...')
    connected_states = remove_duplicate_data_points(connected_states)
    plt.plot_date(list(x[0] for x in connected_states),
                  list(x[1] for x in connected_states),
                  linestyle='-',
                  marker=None)
    logging.info('plot latencies...')
    #latencies = remove_duplicate_data_points(latencies)
    #latencies = convert_to_moving_average(latencies, window_size=30)
    latencies = convert_to_max_of_last_n(latencies, window_size=60)
    plt.plot_date(list(x[0] for x in latencies),
                  list(x[1] for x in latencies),
                  linestyle='-',
                  marker=None)
    logging.info('plot down_speeds...')
    #down_speeds = remove_duplicate_data_points(down_speeds)
    #down_speeds = convert_to_moving_average(down_speeds, window_size=3)
    plt.plot_date(list(x[0] for x in down_speeds),
                  list(x[1] for x in down_speeds),
                  linestyle='-',
                  marker=None)
    logging.info('plot up_speeds...')
    #up_speeds = remove_duplicate_data_points(up_speeds)
    #up_speeds = convert_to_moving_average(up_speeds, window_size=3)
    plt.plot_date(list(x[0] for x in up_speeds),
                  list(x[1] for x in up_speeds),
                  linestyle='-',
                  marker=None)

    plt.ylim([-5, 100])
    formatter = DateFormatter('%m/%d/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=10)

    plt.savefig('graph.png')
    #plt.show()


def save_scatter(two_dimensional_list):

    len_y = len(two_dimensional_list)
    len_x = len(two_dimensional_list[0])

    # y = len(two_dimensional_list)
    # x = len(two_dimensional_list[0])

    x = np.arange(-0.5, len_x)
    y = np.arange(-0.5, len_y)

    # Z = np.random.rand(14 - 1, 8 - 1)
    # x = np.arange(-0.5, 7, 1)  # len = 8
    # y = np.arange(-0.5, 13, 1)  # len = 14

    fig, ax = plt.subplots()
    ax.pcolormesh(x, y, two_dimensional_list)
    plt.show()
    return


class TimedEventsSplitIntoBins():
    def __init__(self):
        pass

    def date_to_bin(self, date):
        """"""
        pass

    def add_event(state, start_date, end_date):
        # lookup bin containing start_date, add a fractional value to that bin
        # 
        # loop through bins and add values until we reach the end_date
        # OR
        # if start_date and end_date are seperated by more than the size of all
        # bins, then add 1 to all bins, until end_date is less than "size of all
        # bins" away. then loop through bins until reaching end_date
        pass


def save_weekly_binned_data_scatter(connected_states):

    time_to_summarize = datetime.timedelta(weeks=1)
    time_per_bin = datetime.timedelta(hours=1)

    num_bins = int(time_to_summarize / time_per_bin)

    cumulative_time_up_bins = list(0 for _ in range(num_bins))
    cumulative_time_down_bins = list(0 for _ in range(num_bins))

    logging.info(f"num_bins:{num_bins}")
    logging.info(f"len(cumulative_time_up_bins):{len(cumulative_time_up_bins)}")
    logging.info(f"cumulative_time_up_bins:{cumulative_time_up_bins}")

    t = TimedEventsSplitIntoBins()

    previous_date = None
    previous_state = None
    for idx, (date, state) in enumerate(connected_states):
        # event that happened spanned from previous_date to date, and previous_state
        # was held true for the entire time span
        t.add_event(previous_state, previous_date, date)
        previous_state = state
        previous_date = date
        pass

    Z = np.random.rand(24, 7)
    save_scatter(Z)
    return

    Z = np.random.rand(14 - 1, 8 - 1)
    x = np.arange(-0.5, 7, 1)  # len = 8
    y = np.arange(-0.5, 13, 1)  # len = 14

    fig, ax = plt.subplots()
    ax.pcolormesh(x, y, Z)
    plt.show()
    return


    fix, ax = plt.subplots()
    yy, xx = numpy.meshgrid(y,x)
    from matplotlib.mlab import griddata
    zz = griddata(x,y,z,xx,yy, interp='linear')
    plt.pcolor(zz)
    plt.contourf(xx,yy,zz) # if you want contour plot
    plt.imshow(zz)
    # plt.pcolormesh()
    ax.pcolormesh(xx, yy, zz)
    plt.show()
    return


def main():

    latencies = []
    down_speeds = []
    up_speeds = []
    connected_states = []

    logging.basicConfig(level=logging.INFO)

    logging.info('load...')
    with open('output.csv', 'r') as handle:
        filesize = handle.seek(0, 2)  # seek to end
        if _CSV_READ_SIZE is None:
            handle.seek(0, 0)  # seek to beginning
        else:
            handle.seek(filesize - _CSV_READ_SIZE, 0)  # seek to CSV_READ_SIZE bytes from the end
        handle.readline()  # throw out the first line: it is probably a partial line

        plots = csv.reader(handle, delimiter=',')
        for row in plots:
            # col 0: date (2020-11-04)
            # col 1: time (17:36:16)
            date = datetime_from_date_and_time_string(row[0], row[1])
            # col 2: latency (16.25)
            if row[2] != '':
                latencies.append((date, float(row[2])))
            # col 3: down speed
            if row[3] != '':
                down_speeds.append((date, float(row[3])))
            # col 4: up speed
            if row[4] != '':
                up_speeds.append((date, float(row[4])))
            # col 5: is connection up? state
            if row[5] != '':
                connected_states.append((date, 1 if row[5] == "True" else 0))

    # preprocess the data

    connected_states = remove_duplicate_data_points(connected_states)

    # summarize dropout stats
    print_dropout_stats(connected_states)

    # plot data over time
    save_data_over_time_graph(connected_states, latencies, down_speeds, up_speeds)

    # plot scatter
    #save_weekly_binned_data_scatter(connected_states)
    return





if __name__ == "__main__":
    main()

