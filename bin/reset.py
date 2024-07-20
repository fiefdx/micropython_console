import sys
import uos
import time
from math import ceil

from scheduler import Condition, Message
from common import exists, path_join, isfile, isdir


def main(*args, **kwargs):
    task = args[0]
    name = args[1]
    result = "invalid parameters"
    shell = kwargs["shell"]
    shell_id = kwargs["shell_id"]
    display_id = shell.display_id
    try:
        lines = [" "*21 for i in range(50)]
        yield Condition(sleep = 0, send_msgs = [
            Message({"clear": True, "output": "\n".join(lines)}, receiver = shell_id)
        ])
    except Exception as e:
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": sys.print_exception(e)}, receiver = shell_id)
        ])


