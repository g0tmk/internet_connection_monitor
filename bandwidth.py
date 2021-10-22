##### UNUSED #####

import requests
import time
import logging


def measure_bandwidth_bytes_per_sec(url):
    """Downloads a file and uses content-length to calculate bytes/sec"""
    start = time.time()
    r = requests.get(url)
    total_length = int(r.headers.get('content-length'))
    end = time.time()
    logging.debug("total_length = {}".format(total_length))
    logging.debug("end - start = {}".format(end - start))
    return total_length / (end - start)


def main():
    # from http://www.engineerhammad.com/2015/04/Download-Test-Files.html
    url1 = "http://speedtest.ftp.otenet.gr/files/test10Mb.db"
    url2 = "http://speedtest.ftp.otenet.gr/files/test100Mb.db"

    # from http://www.thinkbroadband.com/download.html
    url3 = "http://ipv4.download.thinkbroadband.com/10MB.zip"
    url4 = "http://ipv4.download.thinkbroadband.com/100MB.zip"

    # from http://speedtest.tele2.net/
    url5 = "http://speedtest.tele2.net/100MB.zip"

    print("url1={}\nBytes/sec:{}".format(url1, measure_bandwidth_bytes_per_sec(url1)))
    print()
    print("url2={}\nBytes/sec:{}".format(url2, measure_bandwidth_bytes_per_sec(url2)))
    print()
    print("url3={}\nBytes/sec:{}".format(url3, measure_bandwidth_bytes_per_sec(url3)))
    print()
    print("url4={}\nBytes/sec:{}".format(url4, measure_bandwidth_bytes_per_sec(url4)))
    print()
    print("url5={}\nBytes/sec:{}".format(url5, measure_bandwidth_bytes_per_sec(url5)))
    print()


if __name__ == "__main__":
    main()
