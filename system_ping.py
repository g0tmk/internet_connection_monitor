"""Provide an OS-agnostic interface to the ping command."""
import subprocess
import platform

from my_exceptions import NoConnectionException

# The ping timeout. This is also the max measurable ping time output by this module.
# If the connection is down, ping() will take at least this long to report this fact.
_MAX_PING_TIME_SECONDS = 2


def ping(ip, count=1, timeout=_MAX_PING_TIME_SECONDS):
    """Ping an ip and return ping's output, otherwise raise NoConnectionException.."""
    if platform.system().lower() == "windows":
        timeout = int(timeout * 1000)
        timeout = 1 if timeout < 1 else timeout
        ping_params = "-n {} -w {}".format(count, timeout)
    else:
        timeout = int(timeout)
        timeout = 1 if timeout < 1 else timeout
        ping_params = "-c {} -W {}".format(count, timeout)

    cmd = "ping {} {}".format(ping_params, ip)
    try:
        complete_proc = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise NoConnectionException("bad response from ping: server probably down")

    return complete_proc.stdout.decode("utf-8")


if __name__ == "__main__":

    print('check one ip (8.8.8.8):')
    print("ping('8.8.8.8') = ")
    print("=" * 50)
    try:
        print(ping("8.8.8.8"))
    except NoConnectionException:
        print("Got NoConnectionException.")
    print("=" * 50)
