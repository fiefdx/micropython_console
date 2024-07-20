import os
import gc
import sys
import time
import random
from math import ceil
from io import StringIO

from shell import Shell
from scheduler import Condition, Message
from common import exists, path_join, isfile, isdir


def main(*args, **kwargs):
    #print(kwargs["args"])
    task = args[0]
    name = args[1]
    shell = kwargs["shell"]
    shell_id = kwargs["shell_id"]
    display_id = shell.display_id
    cursor_id = shell.cursor_id
    shell.disable_output = True
    shell.enable_cursor = False
    width, height = 21, 9
    try:
        if len(kwargs["args"]) > 2:
            width = int(kwargs["args"][0])
            height = int(kwargs["args"][1])
            size = int(kwargs["args"][2])
            yield Condition(sleep = 0, send_msgs = [
                Message({"clear": True}, receiver = display_id)
            ])
            yield Condition(sleep = 0, send_msgs = [
                Message({"enabled": False}, receiver = cursor_id)
            ])
            data = []
            for h in range(height):
                data.append([])
                for w in range(width):
                    if h % 2 == 0:
                        data[h].append("x" if w % 2 == 0 else "o")
                    else:
                        data[h].append("o" if w % 2 == 0 else "x")
            yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                Message({"bricks": {"data": data, "width": width, "height": height, "size": size}}, receiver = display_id)
            ])
            msg = task.get_message()
            c = msg.content["msg"]
            while c != "ES":
                for h in range(height):
                    for w in range(width):
                        data[h][w] = "x" if data[h][w] == "o" else "o"
                yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                    Message({"bricks": {"data": data, "width": width, "height": height, "size": size}}, receiver = display_id)
                ])
                msg = task.get_message()
                c = msg.content["msg"]
        else:
            yield Condition(sleep = 0, send_msgs = [
                Message({"output": "invalid parameters"}, receiver = shell_id)
            ])
        yield Condition(sleep = 0, send_msgs = [
            Message({"clear": True}, receiver = display_id)
        ])
        yield Condition(sleep = 0, send_msgs = [
            Message({"enabled": True}, receiver = cursor_id)
        ])
        shell.disable_output = False
        shell.enable_cursor = True
        shell.current_shell = None
        yield Condition(sleep = 0, wait_msg = False, send_msgs = [
            Message({"output": ""}, receiver = shell_id)
        ])
    except Exception as e:
        yield Condition(sleep = 0, send_msgs = [
            Message({"clear": True}, receiver = display_id)
        ])
        yield Condition(sleep = 0, send_msgs = [
            Message({"enabled": True}, receiver = cursor_id)
        ])
        shell.disable_output = False
        shell.enable_cursor = True
        shell.current_shell = None
        reason = sys.print_exception(e)
        if reason is None:
            reason = "render failed"
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": str(reason)}, receiver = shell_id)
        ])
        

