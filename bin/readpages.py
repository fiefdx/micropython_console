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
    shell.enable_cursor = False
    width, height = 21, 8
    try:
        pages = []
        frame = []
        read_exit = False
        if len(kwargs["args"]) > 0:
            path = kwargs["args"][0]
            #print("read path: ", path)
            if exists(path) and isfile(path):
                fp = open(path, "r")
                fp.seek(0, 2)
                file_size = fp.tell()
                #print("file_size: ", file_size)
                fp.seek(0)
                row = 1
                pos = fp.tell()
                line = fp.readline()
                pages.append(pos)
                frame_idx = 0
                while not read_exit and line:
                    line_strip = line
                    if line.endswith("\n"):
                        line_strip = line[:-1]
                    col = 1
                    print(row, col, line)
                    if len(line_strip) > 0:
                        for i in range(ceil(len(line_strip) / width)):
                            frame_line = line_strip[i*width:(i+1)*width]
                            frame.append(frame_line)
                            col += len(frame_line)
                            pos += len(frame_line)
                            if i == ceil(len(line_strip) / width) - 1:
                                pos += 1
                            if pos >= file_size:
                                for i in range(height - len(frame)):
                                    frame.append("")
                            if len(frame) == height:
                                frame.append("%s/%s" % (pos, file_size))
                                yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                                    Message({"output_part": "\n".join(frame)}, receiver = shell_id)
                                ])
                                msg = task.get_message()
                                if msg.content["msg"] == "DN":
                                    if fp.tell() < file_size:
                                        frame_idx += 1
                                        if len(pages) > frame_idx:
                                            fp.seek(pages[frame_idx], 0)
                                        else:
                                            pages.append(pos)
                                    else:
                                        frame_idx = len(pages) - 1
                                        fp.seek(pages[frame_idx], 0)
                                elif msg.content["msg"] == "UP":
                                    if frame_idx > 0:
                                        frame_idx -= 1
                                        fp.seek(pages[frame_idx], 0)
                                        pos = pages[frame_idx]
                                    else:
                                        frame_idx = 0
                                        fp.seek(pages[frame_idx], 0)
                                        pos = pages[frame_idx]
                                elif msg.content["msg"] == "ES":
                                    read_exit = True
                                    break
                                #print("msg: ", msg.content, pos, pages)
                                frame = []
                    else:
                        frame.append(line_strip)
                        if line != line_strip:
                            pos += 1
                        if pos >= file_size:
                            for i in range(height - len(frame)):
                                frame.append("")
                        if len(frame) == height:
                            frame.append("%s/%s" % (pos, file_size))
                            yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                                Message({"output_part": "\n".join(frame)}, receiver = shell_id)
                            ])
                            msg = task.get_message()
                            if msg.content["msg"] == "DN":
                                if fp.tell() < file_size:
                                    frame_idx += 1
                                    if len(pages) > frame_idx:
                                        fp.seek(pages[frame_idx], 0)
                                    else:
                                        pages.append(pos)
                                else:
                                    frame_idx = len(pages) - 1
                                    fp.seek(pages[frame_idx], 0)
                            elif msg.content["msg"] == "UP":
                                if frame_idx > 0:
                                    frame_idx -= 1
                                    fp.seek(pages[frame_idx], 0)
                                    pos = pages[frame_idx]
                                else:
                                    frame_idx = 0
                                    fp.seek(pages[frame_idx], 0)
                                    pos = pages[frame_idx]
                            elif msg.content["msg"] == "ES":
                                read_exit = True
                                break
                                
                            #print("msg: ", msg.content, pos, pages)
                            frame = []
                    pos = fp.tell()
                    line = fp.readline()
                    row += 1
                yield Condition(sleep = 0, send_msgs = [
                    Message({"output": ""}, receiver = shell_id)
                ])
                shell.enable_cursor = True
            else:
                yield Condition(sleep = 0, send_msgs = [
                    Message({"output": "%s not file/exists!" % path}, receiver = shell_id)
                ])
                shell.enable_cursor = True
        else:
            yield Condition(sleep = 0, send_msgs = [
                Message({"output": result}, receiver = shell_id)
            ])
            shell.enable_cursor = True
    except Exception as e:
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": sys.print_exception(e)}, receiver = shell_id)
        ])
        shell.enable_cursor = True


