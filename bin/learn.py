import os
import sys
import time
import random
from math import ceil
from io import StringIO

from scheduler import Condition, Message
from common import exists, path_join, isfile, isdir

def count_words(p):
    n = 0
    fp = open(p, "r")
    line = fp.readline()
    while line:
        line = line.strip()
        if line:
            n += 1
        line = fp.readline()
    fp.close()
    return n


def select_words(p, ids = []):
    words = []
    n = 0
    fp = open(p, "r")
    line = fp.readline()
    while line:
        line = line.strip()
        if line:
            if n in ids:
                words.append(line)
            n += 1
        line = fp.readline()
    fp.close()
    return words


def main(*args, **kwargs):
    #print(kwargs["args"])
    task = args[0]
    name = args[1]
    shell = kwargs["shell"]
    shell_id = kwargs["shell_id"]
    display_id = shell.display_id
    shell.disable_output = True
    shell.enable_cursor = False
    width, height = 21, 9
    if len(kwargs["args"]) > 2:
        word_list, random_offset, limit = kwargs["args"]
        limit = int(limit)
        try:
            words_file_path = path_join("/sd/dict", "%s.words" % word_list)
            words_total = count_words(words_file_path)
            words_ids = []
            if random_offset == "r": # random
                for i in range(limit):
                    word_i = random.randint(0, words_total - 1)
                    while word_i in words_ids:
                        word_i = random.randint(0, words_total - 1)
                    words_ids.append(word_i)
            else:
                offset = int(random_offset)
                words_ids = [i for i in range(offset, offset + limit)]
            words = select_words(words_file_path, ids = words_ids)
            learn_exit = False
            i = 0
            while not learn_exit:
                frame = []
                word = words[i]
                word_mask = []
                for m in range(int(len(word)/2)):
                    mi = random.randint(0, len(word) - 1)
                    while mi in word_mask:
                        mi = random.randint(0, len(word) - 1)
                    word_mask.append(mi)
                word_with_mask = ""
                for mi, c in enumerate(word):
                    if mi in word_mask:
                        word_with_mask += "_"
                    else:
                        word_with_mask += c
                frame.append(word_with_mask)
                #frame.append("%03d/%03d              " % (i + 1, len(words)))
                defination = []
                d = 0
                with open(path_join("/sd/dict", word_list, "%s.txt" % word.replace(" ", "_")), "r") as fp:
                    line = fp.readline()
                    line = fp.readline()
                    while line:
                        line = line.replace("\r", "")
                        line = line.replace("\n", "")
                        display_line = line[:width]
                        while display_line:
                            defination.append(display_line)
                            line = line[width:]
                            display_line = line[:width]
                        line = fp.readline()
                for f in range(height - 1):
                    if f < len(defination[d:]):
                        frame.append(defination[d:][f])
                    else:
                        frame.append(" " * width)
                #frame[-1] = "%12s  %03d/%03d" % (frame[-1][:12].ljust(12), i + 1, len(words))
                frame[-1] = "{: <12}  {:0>3}/{:0>3}".format(frame[-1][:12], i + 1, len(words))
                yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                    Message({"frame": frame}, receiver = display_id)
                ])
                msg = task.get_message()
                c = msg.content["msg"]
                reveal = False
                while c != "":
                    if c == "ES":
                        learn_exit = True
                        break
                    elif c == "RT":
                        i += 1
                        if i >= len(words):
                            i = 0
                        break
                    elif c == "LT":
                        i -= 1
                        if i <= 0:
                            i = 0
                        break
                    elif c in ("DN", "UP", "\n"):
                        if c == "DN":
                            d += 1
                            if d >= len(defination):
                                d = len(defination) - 1
                        elif c == "UP":
                            d -= 1
                            if d <= 0:
                                d = 0
                        elif c == "\n":
                            reveal = not reveal
                        frame = []
                        if reveal:
                            frame.append(word)
                        else:
                            frame.append(word_with_mask)
                        #frame.append("%03d/%03d              " % (i + 1, len(words)))
                        for f in range(height - 1):
                            if f < len(defination[d:]):
                                frame.append(defination[d:][f])
                            else:
                                frame.append(" " * width)
                        #frame[-1] = "%12s  %03d/%03d" % (frame[-1][:12].ljust(12), i + 1, len(words))
                        frame[-1] = "{: <12}  {:0>3}/{:0>3}".format(frame[-1][:12], i + 1, len(words))
                        yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                            Message({"frame": frame}, receiver = display_id)
                        ])
                    yield Condition(sleep = 0, wait_msg = True)
                    msg = task.get_message()
                    c = msg.content["msg"]

            #print("password:", password)
            shell.disable_output = False
            shell.current_shell = None
            shell.enable_cursor = True
            yield Condition(sleep = 0, wait_msg = False, send_msgs = [
                Message({"output": "quit"}, receiver = shell_id)
            ])
        except Exception as e:
            shell.disable_output = False
            shell.current_shell = None
            shell.enable_cursor = True
            yield Condition(sleep = 0, send_msgs = [
                Message({"output": sys.print_exception(e)}, receiver = shell_id)
            ])
    else:
        shell.disable_output = False
        shell.current_shell = None
        shell.enable_cursor = True
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": "invalid parameters"}, receiver = shell_id)
        ])
