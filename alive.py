##### UNUSED #####

from multiprocessing import Pool

import system_ping

_MAX_THREADS = 5


def alive(ip):
    try:
        system_ping.ping(ip, count=1, timeout=1)
    except system_ping.NoConnectionException:
        return False
    return True


def alive_list(ip_list, repeat_forever=False):
    """Check if IPs are alive using threads"""
    with Pool(_MAX_THREADS) as p:
        raw_results = p.map_async(alive, ip_list).get(999)

    all_alive = all(raw_results)

    return all_alive, list(zip(ip_list, raw_results))


if __name__ == "__main__":

    ips = ["10.0.0.1", "138.229.248.1", "8.8.8.8"]

    print('check multiple ips')
    print("  alive_list([\"10.0.0.1\", \"138.229.248.1\", \"8.8.8.8\"]) = ", alive_list(ips))

    print('check one ip')
    print("  alive('8.8.8.8') = ", alive('8.8.8.8'))

    print('check a down IP')
    print("  alive('10.234.123.123') = ", alive('10.234.123.123'))

