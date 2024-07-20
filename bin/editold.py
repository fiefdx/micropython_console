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

class EditShell(object):
    def __init__(self, file_path, display_size = (21, 9), cache_size = 8):
        self.display_width = display_size[0]
        self.display_height = display_size[1]
        self.offset_col = 0
        self.offset_row = 0
        self.cache_size = cache_size
        self.cache = []
        self.lines_pos = []
        self.cursor_color = 1
        self.cursor_row = 0
        self.cursor_col = 0
        self.enable_cursor = True
        self.exit = False
        self.file_path = file_path
        self.file = open(self.file_path, "r")
        self.total_lines = 0
        self.calc_total_lines()
        self.line_num = 0
        
    def input_char(self, c):
        if c == "\n":
            pass
        elif c == "\b":
            pass
        elif c == "UP":
            self.cursor_move_up()
        elif c == "DN":
            self.cursor_move_down()
        elif c == "LT":
            self.cursor_move_left()
        elif c == "RT":
            self.cursor_move_right()
        elif c == "SAVE":
            print("save:", self.file_path)
        elif c == "ES":
            self.exit = True
        else:
            pass
        
    def calc_total_lines(self):
        n = 0
        pos = self.file.tell()
        line = self.file.readline()
        while line:
            if n % 10 == 0:
                self.lines_pos.append(pos)
            n += 1
            if n % 100 == 0:
                gc.collect()
            pos = self.file.tell()
            line = self.file.readline()
        self.file.seek(0)
        self.total_lines = n
        
    def exists_line(self, line_num):
        return line_num >= 0 and line_num < self.total_lines
    
    def load_cache(self, line_num):
        if self.exists_line(line_num):
            start_pos_idx = int(line_num / 10)
            skip_lines = line_num % 10
            self.file.seek(self.lines_pos[start_pos_idx])
            self.cache = []
            for i in range(skip_lines):
                self.file.readline()
            for l in range(self.cache_size):
                line = self.file.readline()
                #print("load_cache:", line)
                if line:
                    line = line.replace("\r", "")
                    line = line.replace("\n", "")
                    self.cache.append(line)
                else:
                    self.cache.append("")
            
    def get_display_frame(self):
        return self.cache_to_frame()
            
    def cache_to_frame(self):
        frame = []
        for line in self.cache:
            frame.append(line[self.offset_col: self.offset_col + self.display_width])
        frame.append("%s/%s/%s" % (self.cursor_col + self.offset_col, self.line_num + self.cursor_row + 1, self.total_lines))
        return frame
    
    def get_cursor_position(self, c = None):
        return self.cursor_col, self.cursor_row, self.cursor_color if c is None else c
    
    def set_cursor_color(self, c):
        self.cursor_color = c
            
    def cursor_move_up(self):
        self.cursor_row -= 1
        if self.cursor_row < 0:
            if self.line_num > 0:
                self.line_num -= 1
                self.load_cache(self.line_num)
            self.cursor_row = 0
    
    def cursor_move_down(self):
        self.cursor_row += 1
        if self.cursor_row > self.cache_size - 1:
            if self.line_num < self.total_lines - self.cache_size:
                self.line_num += 1
                self.load_cache(self.line_num)
            self.cursor_row = self.cache_size - 1
    
    def cursor_move_left(self):
        self.cursor_col -= 1
        if self.cursor_col < 0:
            if self.offset_col > 0:
                self.offset_col -= 1
                self.cache_to_frame()
            self.cursor_col = 0
        
    def cursor_move_right(self):
        self.cursor_col += 1
        if len(self.cache[self.cursor_row]) >= self.cursor_col + self.offset_col:
            if self.cursor_col > self.display_width:
                self.offset_col += 1
                self.cache_to_frame()
                self.cursor_col = self.display_width
        else:
            self.cursor_col -= 1
            
    def close(self):
        self.file.close()

def main(*args, **kwargs):
    #print(kwargs["args"])
    task = args[0]
    name = args[1]
    shell = kwargs["shell"]
    shell_id = kwargs["shell_id"]
    display_id = shell.display_id
    shell.disable_output = True
    width, height = 21, 9
    try:
        if len(kwargs["args"]) > 0:
            file_path = kwargs["args"][0]
            if exists(file_path):
                s = EditShell(file_path)
                shell.current_shell = s
                line_num = 0
                s.load_cache(line_num)
                yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                    Message({"frame": s.get_display_frame(), "cursor": s.get_cursor_position(1)}, receiver = shell_id)
                ])
                msg = task.get_message()
                c = msg.content["msg"]
                while not s.exit:
                    s.input_char(c)
                    if s.exit:
                        break
                    yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                        Message({"frame": s.get_display_frame(), "cursor": s.get_cursor_position(1)}, receiver = shell_id)
                    ])
                    msg = task.get_message()
                    c = msg.content["msg"]
            else:
                yield Condition(sleep = 0, send_msgs = [
                    Message({"output": "invalid parameters"}, receiver = shell_id)
                ])
        else:
            yield Condition(sleep = 0, send_msgs = [
                Message({"output": "invalid parameters"}, receiver = shell_id)
            ])
        shell.disable_output = False
        shell.current_shell = None
        yield Condition(sleep = 0, wait_msg = False, send_msgs = [
            Message({"output": ""}, receiver = shell_id)
        ])
    except Exception as e:
        shell.disable_output = False
        shell.current_shell = None
        reason = sys.print_exception(e)
        if reason is None:
            reason = "edit failed"
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": str(reason)}, receiver = shell_id)
        ])
        
