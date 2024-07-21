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
    width, height = 128, 64
    try:
        if len(kwargs["args"]) > 0:
            interval = int(kwargs["args"][0])
            yield Condition(sleep = 0, send_msgs = [
                Message({"clear": True}, receiver = display_id)
            ])
            yield Condition(sleep = 0, send_msgs = [
                Message({"enabled": False}, receiver = cursor_id)
            ])
            frames_path = "/sd/tmp/badapple/frames-8864-15fps-compressed-txt/frames.txt"
            fp = open(frames_path, "r")
            #f_max = 2191
            f_max = 3286
            #f_max = 4381
            f = 1
            frame_data = eval(fp.readline())
            yield Condition(sleep = interval, wait_msg = False, send_msgs = [
                Message({"binary": frame_data, "x": 20, "y": 0, "width": 88, "height": 64, "invert": True}, receiver = display_id)
            ])
            c = None
            msg = task.get_message()
            if msg:
                c = msg.content["msg"]
            end = False
            while c != "ES" and not end:
                f += 1
                if f > f_max:
                    f = 1
                    end = True
                else:
                    frame_data = eval(fp.readline())
                    yield Condition(sleep = interval, wait_msg = False, send_msgs = [
                        Message({"binary": frame_data, "x": 20, "y": 0, "width": 88, "height": 64, "invert": True}, receiver = display_id)
                    ])
                msg = task.get_message()
                if msg:
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
