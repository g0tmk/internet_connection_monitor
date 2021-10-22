import logging
import time
import datetime
import sys
import math

from ping_wrapper import ping
from my_exceptions import NoConnectionException

import speedtest

_LATENCY_IP = "8.8.8.8"
_PING_SAMPLE_COUNT = 2
_OUTPUT_CSV = "./output.csv"
# How often to print a new line (otherwise overwrite). A new line is always printed on disconnect.
_PRINT_RATE = 300


if (sys.version_info < (3, 6)):
    print("This requires python 3.6+")
    sys.exit(1)


class StatefulConsolePrinter:
    def __init__(self):
        self.previous_state_was_up = None
        self.latest_latency = ""
        self.latest_down_bandwidth = ""
        self.latest_up_bandwidth = ""
        self.next_print_unixtime = None

    def print_data_to_console(self, date_time, latency, down_bandwidth, up_bandwidth, state_is_up):

        # overwrite latest data if its provided
        if latency != "":
            self.latest_latency = latency
        if down_bandwidth != "":
            self.latest_down_bandwidth = down_bandwidth
        if up_bandwidth != "":
            self.latest_up_bandwidth = up_bandwidth

        # determine if we should print a new line - do it if state changes / a min passes
        should_print_new_line = False
        if self.previous_state_was_up is None:
            should_print_new_line = True
        if state_is_up == True and self.previous_state_was_up == False:
            should_print_new_line = True
        if state_is_up == False and self.previous_state_was_up == True:
            should_print_new_line = True

        if (self.next_print_unixtime is None
                or date_time.timestamp() >= self.next_print_unixtime):
            self.next_print_unixtime = date_time.timestamp() + _PRINT_RATE - (date_time.timestamp() % _PRINT_RATE)
            should_print_new_line = True

        # if inet goes down, clear the latency/speed info
        if state_is_up == False:
            self.latest_latency = ""
            self.latest_down_bandwidth = ""
            self.latest_up_bandwidth = ""

        line = "{} {} {:>9} {:>7} {:>7}  {:5}".format(
            date_time.strftime("%m-%d"),
            date_time.strftime("%H:%M:%S"),
            self.latest_latency+' ms' if self.latest_latency != "" else "",
            self.latest_down_bandwidth+'↓' if self.latest_down_bandwidth != "" else "",
            self.latest_up_bandwidth+'↑' if self.latest_up_bandwidth != "" else "",
            "UP" if state_is_up else "DOWN!"
        )
        line = line.ljust(70)  # pad to some len with " " chars to overwrite previous line

        print(line, end='\n' if should_print_new_line else '\r')

        self.previous_state_was_up = state_is_up


printer = StatefulConsolePrinter()
def save_to_csv(date_time=None, latency="", down_bandwidth="", up_bandwidth="", state_is_up=""):
    global printer
    if date_time is None:
        date_time = datetime.datetime.now()
    with open(_OUTPUT_CSV, "a") as handle:
        print(
            "{},{},{},{},{},{}".format(
                date_time.strftime("%Y-%m-%d"),
                date_time.strftime("%H:%M:%S"),
                latency,
                down_bandwidth,
                up_bandwidth,
                state_is_up
            ),
            file=handle)

    printer.print_data_to_console(date_time, latency, down_bandwidth, up_bandwidth, state_is_up)


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

            logging.debug("Missed {:.0f} timers".format(
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
        # logging.info("LATENCY    : no connection")
        save_to_csv(state_is_up=False)
    else:
        # logging.info("LATENCY    : {:.2f} ms to {}".format(latency, ip))
        save_to_csv(state_is_up=True, latency="{:.2f}".format(latency))


def log_bandwidth():
    try:
        download = speedtest.Speedtest().download()
        upload = speedtest.Speedtest().upload()
    except speedtest.SpeedtestHTTPError:
        # logging.info("BANDWIDTH  : no connection")
        save_to_csv(state_is_up=False)
    else:
        # logging.info("BANDWIDTH  : {:.2f} mbits down {:.2f} mbits up".format(download / 1000000, upload / 1000000))
        save_to_csv(state_is_up=True,
                    down_bandwidth="{:.2f}".format(download / 1000000),
                    up_bandwidth="{:.2f}".format(upload / 1000000))


def run_events(event_list):
    for e in event_list:
        e.run()


def monitor_forever(ping_ip):
    event_list = [
        PeriodicEvent(2, lambda i=ping_ip: log_latency(i)),
        PeriodicEvent(600, lambda: log_bandwidth())
    ]

    while(True):
        try:
            time.sleep(1.0)
            run_events(event_list)
        except (KeyboardInterrupt, SystemExit):
            logging.info("exiting")
            break
        except Exception as e:
            logging.exception("Exception thrown while checking connection, waiting 10s...")
            time.sleep(10)


def main():
    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s",
                        level=logging.DEBUG,
                        filename='debug.log')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    monitor_forever(ping_ip=_LATENCY_IP)


if __name__ == "__main__":
    main()
