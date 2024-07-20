import time

from wifi import WIFI
from scheduler import Condition, Message


def main(*args, **kwargs):
    task = args[0]
    name = args[1]
    shell_id = kwargs["shell_id"]
    try:
        WIFI.active(True)
        yield Condition(sleep = 0, send_msgs = [
            Message({"output_part": "connect to: %s" % WIFI.ssid}, receiver = shell_id)
        ])
        WIFI.reconnect()
        s = time.time()
        while not WIFI.is_connect():
            yield Condition(sleep = 1000, send_msgs = [
                Message({"output_part": "connecting ..."}, receiver = shell_id)
            ])
            ss = time.time()
            if ss - s >= 10:
                yield Condition(sleep = 1000, send_msgs = [
                    Message({"output_part": "connecting too long, check ifconfig later!"}, receiver = shell_id)
                ])
                break
        if WIFI.is_connect():
            yield Condition(sleep = 1000, send_msgs = [
                Message({"output": "\n".join(WIFI.ifconfig())}, receiver = shell_id)
            ])
        else:
            yield Condition(sleep = 0, send_msgs = [
                Message({"output": "connect to %s failed" % WIFI.ssid}, receiver = shell_id)
            ])
    except Exception as e:
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": sys.print_exception(e)}, receiver = shell_id)
        ])
