import time

from wifi import WIFI
from scheduler import Condition, Message


def main(*args, **kwargs):
    task = args[0]
    name = args[1]
    result = "invalid parameters"
    shell_id = kwargs["shell_id"]
    try:
        if len(kwargs["args"]) > 0:
            ssid = kwargs["args"][0]
            WIFI.active(True)
            yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                Message({"output_part": "password:"}, receiver = shell_id)
            ])
            password = ""
            msg = task.get_message()
            while msg.content["msg"] != "\n":
                if msg.content["msg"] == "\b":
                    password = password[:-1]
                else:
                    password += msg.content["msg"]
                yield Condition(sleep = 0, wait_msg = True)
                msg = task.get_message()
            #print("password:", password)
            WIFI.connect(ssid, password)
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
                    Message({"output": "connect to %s failed" % ssid}, receiver = shell_id)
                ])
        else:
            yield Condition(sleep = 0, send_msgs = [
                Message({"output": result}, receiver = shell_id)
            ])
    except Exception as e:
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": sys.print_exception(e)}, receiver = shell_id)
        ])

