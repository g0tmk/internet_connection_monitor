#!/usr/bin/env python2.5
import re
from multiprocessing import Pool

from system_ping import ping

# a number too high may affect ping times
_MAX_THREADS = 5


def measure_latency_with_count(ip_count_tuple):
    ip, repeat_count = ip_count_tuple

    lines = ping(ip, count=repeat_count).splitlines()

    if len(lines) < 3:
        raise RuntimeError("bad response from ping: not enough lines")

    values = []
    for line in lines:
        # should match both unix/win ping: optional space before ms
        #   "time=10.0 ms"  unix
        #   "time=<1ms"     windows
        #   "time=10.0ms"   windows
        match = re.search("time=?([<\d.]+) ?ms", line)
        if match:
            # Windows shows all values lower than 1ms as "<1ms"
            value = 0.5 if match.group(1) == "<1" else match.group(1)
            values.append(value)

    if len(values) != repeat_count:
        raise RuntimeError("bad response from ping: wrong number of matches ({})".format(len(values)))

    total = sum(float(n) for n in values)
    return total / repeat_count


def measure_latency_list(ip_list, repeat_count=10):
    """Check latencies using threads. Returns a list of (address, ping in ms) tuples."""

    ip_count_list = [(ip, repeat_count) for ip in ip_list]

    with Pool(_MAX_THREADS) as p:
        raw_results = p.map_async(measure_latency_with_count, ip_count_list).get(999)

    return list(zip(ip_list, raw_results))


if __name__ == "__main__":

    print("two parallel pings to 10.0.0.1 and 8.8.8.8:")
    print("measure_latency_list(['10.0.0.1','8.8.8.8']) = {}".format(measure_latency_list(['10.0.0.1','8.8.8.8'])))
    print()
    print("{} parallel ping operations (max thread count) to 8.8.8.8:".format(_MAX_THREADS))
    print("measure_latency_list(['8.8.8.8']*{}) = {}".format(_MAX_THREADS, measure_latency_list(['8.8.8.8']*_MAX_THREADS)))
    print()
    print("{} parallel ping operations (max thread count) to 8.8.8.8, one sample each:".format(_MAX_THREADS))
    print("measure_latency_list(['8.8.8.8']*{}, count=1) = {}".format(_MAX_THREADS, measure_latency_list(['8.8.8.8']*_MAX_THREADS, repeat_count=1)))
