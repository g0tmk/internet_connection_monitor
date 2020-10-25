#!/usr/bin/env python2.5
import re
from multiprocessing import Pool

from system_ping import ping, NoConnectionException

# a number too high may affect ping times
_MAX_THREADS = 5


def measure_latency_with_count(ip_count_tuple):
    ip, count = ip_count_tuple
    try:
        output = ping(ip, count=count)
    except NoConnectionException:
        return None

    # for windows: remove \r
    output = output.replace("\r", "")

    lines = re.split('\n', output)
    lines = list(filter(None, lines))

    if len(lines) < 2:
        raise RuntimeError("bad response from ping: not enough lines")

    # first line is always status/title only
    lines = lines[1:]

    #print(lines)
    values = []
    for line in lines:
        # should match both unix/win ping: optional space before ms
        #   "time=10.0 ms"  unix
        #   "time=<1ms"     windows
        #   "time=10.0ms"   windows
        match = re.search("time=?([<\d.]+) ?ms", line)
        if match:
            values.append(match.group(1))
        else:
            pass

    if len(values) != count:
        raise RuntimeError("bad response from ping: wrong number of matches ({})".format(repr(matches)))

    total = 0.0
    for val in values:
        # Windows shows all values lower than 1ms as "<1ms"
        if val == "<1":
            val = 0.5
        total += float(val)
    return total / count


def measure_latency_list(ip_list, count=10):
    """Check latencies using threads. Returns a list of (address, ping in ms) tuples."""

    ip_count_list = [(ip, count) for ip in ip_list]

    with Pool(_MAX_THREADS) as p:
        raw_results = p.map_async(measure_latency_with_count, ip_count_list).get(999)

    return list(zip(ip_list, raw_results))


if __name__ == "__main__":

    #latency_in_ms = measure_latency("8.8.8.8")
    #print("measure_latency('8.8.8.8') = {:.2f} ms".format(latency_in_ms))

    print("two parallel pings to 10.0.0.1 and 8.8.8.8:")
    print("measure_latency_list(['10.0.0.1','8.8.8.8']) = {}".format(measure_latency_list(['10.0.0.1','8.8.8.8'])))
    print()
    print("{} parallel ping operations (max thread count) to 8.8.8.8:".format(_MAX_THREADS))
    print("measure_latency_list(['8.8.8.8']*{}) = {}".format(_MAX_THREADS, measure_latency_list(['8.8.8.8']*_MAX_THREADS)))
    print()
    print("{} parallel ping operations (max thread count) to 8.8.8.8, one sample each:".format(_MAX_THREADS))
    print("measure_latency_list(['8.8.8.8']*{}, count=1) = {}".format(_MAX_THREADS, measure_latency_list(['8.8.8.8']*_MAX_THREADS, count=1)))
