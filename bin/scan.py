import time

from wifi import WIFI
from scheduler import Condition, Message


def main(*args, **kwargs):
    task = args[0]
    name = args[1]
    result = "invalid parameters"
    shell_id = kwargs["shell_id"]
    try:
        for ssid in WIFI.scan():
            yield Condition(sleep = 0, send_msgs = [
                Message({"output_part": ssid[0].decode("utf-8")}, receiver = shell_id)
            ])
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": ""}, receiver = shell_id)
        ])
    except Exception as e:
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": sys.print_exception(e)}, receiver = shell_id)
        ])
