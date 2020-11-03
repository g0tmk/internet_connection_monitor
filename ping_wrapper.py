"""Provide an OS-agnostic interface to the ping command."""
import subprocess
import platform
import re
from multiprocessing import Pool

from my_exceptions import NoConnectionException

# The ping timeout. This is also the max measurable ping time output by this module.
# If the connection is down, ping() will take at least this long to report this fact.
_MAX_PING_TIME_SECONDS = 2

# a number too high may affect ping times for ping_parallel()
_MAX_THREADS_FOR_PARALLEL_PING = 5


def ping(ip, sample_count=2):
    """Ping an IP, return its average latency."""
    latencies = ping_and_return_latency_list(ip, sample_count)
    return sum(latencies) / len(latencies)  # average


def ping_parallel(ip_list, sample_count=2):
    """Check latency to multiple IPs in parallel. 

    Returns a list of (address, ping in ms) tuples."""

    ip_count_list = [(ip, sample_count) for ip in ip_list]

    with Pool(_MAX_THREADS_FOR_PARALLEL_PING) as p:
        raw_results = p.map_async(ping_with_wrapped_parameters,
                                  ip_count_list).get(999)

    return list(zip(ip_list, raw_results))


def ping_and_return_latency_list(ip, sample_count=2):
    """Ping an IP, return a list of latencies in ms, one per sample_count."""
    lines = ping_and_return_text_output(ip, sample_count=sample_count).splitlines()

    # TODO: replace with a real check once I see the error message
    if "Error resolving network or something" in lines:
        raise NoConnectionException("Ping contained an error message but still returned success..?")

    if len(lines) < 3:
        raise RuntimeError(
            "Not enough lines from ping (output={})".format(repr(lines)))

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

    if len(values) != sample_count:
        raise RuntimeError(
            "Wrong number of matches ({}) from ping (output={})".format(len(values),
                                                                        repr(lines)))

    return list(float(n) for n in values)


def ping_and_return_text_output(ip, sample_count=1, timeout=_MAX_PING_TIME_SECONDS):
    """Ping an ip and return ping's output, otherwise raise NoConnectionException.."""
    if platform.system().lower() == "windows":
        timeout = int(timeout * 1000)
        timeout = 1 if timeout < 1 else timeout
        ping_params = "-n {} -w {}".format(sample_count, timeout)
    else:
        timeout = int(timeout)
        timeout = 1 if timeout < 1 else timeout
        ping_params = "-c {} -W {}".format(sample_count, timeout)

    cmd = "ping {} {}".format(ping_params, ip)
    try:
        complete_proc = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise NoConnectionException("bad response from ping: server probably down")

    return complete_proc.stdout.decode("utf-8")


def ping_with_wrapped_parameters(ip_count_tuple):
    ip, sample_count = ip_count_tuple
    return ping(ip, sample_count=sample_count)


if __name__ == "__main__":

    
    try:
        print("ping('8.8.8.8') = {}".format(ping("8.8.8.8")))
    except NoConnectionException:
        print("ping('8.8.8.8') = {}".format("Got NoConnectionException."))

    try:
        print("ping_and_return_latency_list('8.8.8.8') = {}".format(
            repr(ping_and_return_latency_list("8.8.8.8"))))
    except NoConnectionException:
        print("ping_and_return_latency_list('8.8.8.8') = {}".format(
            "Got NoConnectionException."))

    print("two parallel pings to 10.0.0.1 and 8.8.8.8:")
    print("ping_parallel(['10.0.0.1','8.8.8.8']) = {}".format(ping_parallel(['10.0.0.1','8.8.8.8'])))
    print()
    print("{} parallel ping operations (max thread count) to 8.8.8.8:".format(_MAX_THREADS_FOR_PARALLEL_PING))
    print("ping_parallel(['8.8.8.8']*{}) = {}".format(_MAX_THREADS_FOR_PARALLEL_PING, ping_parallel(['8.8.8.8']*_MAX_THREADS_FOR_PARALLEL_PING)))
    print()
    print("{} parallel ping operations (max thread count) to 8.8.8.8, one sample each:".format(_MAX_THREADS_FOR_PARALLEL_PING))
    print("ping_parallel(['8.8.8.8']*{}, sample_count=1) = {}".format(_MAX_THREADS_FOR_PARALLEL_PING, ping_parallel(['8.8.8.8']*_MAX_THREADS_FOR_PARALLEL_PING, sample_count=1)))
