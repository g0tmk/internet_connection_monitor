import logging
import time
import datetime
import sys
import math

from ping_wrapper import ping
from my_exceptions import NoConnectionException

import speedtest

_BANDWIDTH_URL = "http://ipv4.download.thinkbroadband.com/2MB.zip"
_LATENCY_IP = "8.8.8.8"
_PING_SAMPLE_COUNT = 2
_OUTPUT_CSV = "./output.csv"


if (sys.version_info < (3, 6)):
    print("This requires python 3.6+")
    sys.exit(1)


def save_to_csv(date=None, time=None, latency="", down_bandwidth="", up_bandwidth="", state_is_up=""):
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    if time is None:
        time = datetime.datetime.now().strftime("%H:%M:%S")
    with open(_OUTPUT_CSV, "a") as handle:
        print(f"{date},{time},{latency},{down_bandwidth},{up_bandwidth},{state_is_up}", file=handle)


class PeriodicEvent():
    def __init__(self, period_in_secs, callback):
        self.period = period_in_secs
        self.callback = callback
        self.next_run = time.time()

    def reset_timer(self):
        time_now = time.time()

        self.next_run += self.period

        if self.next_run < time_now:
            # if the next planned run time is in the past, we skipped at least one
            # update period somehow - probably by pausing the program or putting the
            # computer in sleep mode.
            seconds_lost = time_now - self.next_run
            number_of_missed_periods = math.floor(seconds_lost / self.period) + 1

            # logging.info("time_now:      {}".format(time_now))
            # logging.info("self.next_run: {}".format(self.next_run))
            # logging.info("seconds_lost:  {}".format(seconds_lost))

            logging.info("Missed {:.0f} timers".format(
                number_of_missed_periods))

            self.next_run += (self.period * number_of_missed_periods)

    def is_timer_expired(self, auto_reset=True):
        now = time.time()
        if now > self.next_run:
            if auto_reset:
                self.reset_timer()
            return True
        return False

    def run(self):
        if self.is_timer_expired():
            self.callback()


def log_latency(ip):
    try:
        latency = ping(ip, _PING_SAMPLE_COUNT)
    except NoConnectionException:
        logging.info("LATENCY    : no connection")
        save_to_csv(state_is_up=False)
    else:
        logging.info("LATENCY    : {:.2f} ms to {}".format(latency, ip))
        save_to_csv(state_is_up=True, latency="{:.2f}".format(latency))


def log_bandwidth(url):
    try:
        download = speedtest.Speedtest().download()
        upload = speedtest.Speedtest().upload()
    except speedtest.SpeedtestHTTPError:
        logging.info("BANDWIDTH  : no connection")
        save_to_csv(state_is_up=False)
    else:
        logging.info("BANDWIDTH  : {:.3f} mbits down {:.3f} mbits up".format(download / 1000000, upload / 1000000))
        save_to_csv(down_bandwidth="{:.3f}".format(download / 1000000),
                    up_bandwidth="{:.3f}".format(upload / 1000000),
                    state_is_up=True)


def run_events(event_list):
    for e in event_list:
        e.run()


def monitor_forever(ip=_LATENCY_IP,
                    bandwidth_url=_BANDWIDTH_URL):
    event_list = [
        PeriodicEvent(10, lambda i=ip: log_latency(i)),
        PeriodicEvent(600, lambda u=bandwidth_url: log_bandwidth(u))
    ]

    while(True):
        try:
            time.sleep(1.0)
            run_events(event_list)
        except (KeyboardInterrupt, SystemExit):
            logging.info("Bye!")
            break
        except Exception as e:
            logging.exception("Exception thrown while checking connection, waiting 10s...")


def main():
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s",
                        level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    monitor_forever()


if __name__ == "__main__":
    main()
