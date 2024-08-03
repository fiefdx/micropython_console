import os
import sys
import time
from math import ceil
from io import StringIO

from shell import Shell
from scheduler import Condition, Message
from common import exists, path_join, isfile, isdir, path_split

class PyShell(Shell):
    def __init__(self, display_size = (19, 9), cache_size = (-1, 30), history_length = 50, prompt_c = ">>>", scheduler = None, display_id = None, storage_id = None, history_file_path = "/.python_history"):
        self.display_width = display_size[0]
        self.display_height = display_size[1]
        self.display_width_with_prompt = display_size[0] + len(prompt_c)
        self.history_length = history_length
        self.prompt_c = prompt_c
        self.history = []
        self.cache_width = cache_size[0]
        self.cache_lines = cache_size[1]
        self.cache = []
        self.cursor_color = 1
        self.current_row = 0
        self.current_col = 0
        self.scheduler = scheduler
        self.display_id = display_id
        self.storage_id = storage_id
        self.cursor_row = 0
        self.cursor_col = 0
        self.history_idx = 0
        self.scroll_row = 0
        self.frame_history = []
        self.session_task_id = None
        self.exit = False
        self.current_shell = None
        self.enable_cursor = True
        self.history_file_path = history_file_path
        self.load_history()
        self.clear()
        #Shell.__init__(self, display_size = display_size, cache_size = cache_size, history_length = history_length, prompt_c = prompt_c, scheduler = scheduler, display_id = display_id, storage_id = storage_id)
        #self.session_task_id = None
        #self.exit = False
        #self.current_shell = None
        
    def clear(self):
        self.term = StringIO()
        os.dupterm(self.term)
        
    def exec_script(self, script, args = []):
        try:
            exec(script, {"args": args})
        except Exception as e:
            print(sys.print_exception(e))
        self.term.seek(0)
        lines = self.term.read().strip()
        lines = lines.replace("\r", "")
        self.clear()
        return lines
        
    def input_char(self, c):
        if c == "\n":
            cmd = self.cache[-1][len(self.prompt_c):].strip()
            if len(cmd) > 0:
                self.history.append(self.cache[-1][len(self.prompt_c):])
                self.write_history(self.cache[-1][len(self.prompt_c):])
                if cmd == "quit()":
                    self.exit = True
                    os.dupterm(None)
                else:
                    if "=" in cmd or "for" in cmd or "import" in cmd or "from" in cmd or "if" in cmd:
                        try:
                            exec(cmd)
                        except Exception as e:
                            print(sys.print_exception(e))
                        self.term.seek(0)
                        lines = self.term.read().strip()
                        lines = lines.replace("\r", "")
                        self.write_lines(lines, end = True)
                        self.clear()
                    else:
                        try:
                            s = eval(cmd)
                            if s is not None:
                                self.write_lines(str(s).strip(), end = True)
                            else:
                                self.term.seek(0)
                                lines = self.term.read().strip()
                                lines = lines.replace("\r", "")
                                self.write_lines(lines, end = True)
                                self.clear()
                        except Exception as e:
                            print(sys.print_exception(e))
                            self.term.seek(0)
                            lines = self.term.read().strip()
                            lines = lines.replace("\r", "")
                            self.write_lines(lines, end = True)
                            self.clear()
            else:
                self.cache.append(self.prompt_c)
                self.cache_to_frame_history()
            if len(self.history) > self.history_length:
                self.history.pop(0)
            self.history_idx = len(self.history)
        elif c == "\b":
            if len(self.cache[-1][:self.current_col]) > len(self.prompt_c):
                self.cache[-1] = self.cache[-1][:self.current_col-1] + self.cache[-1][self.current_col:]
                self.cursor_move_left()
        elif c == "SUP":
            self.scroll_up()
        elif c == "SDN":
            self.scroll_down()
        elif c == "UP":
            self.history_previous()
        elif c == "DN":
            self.history_next()
        elif c == "LT":
            self.cursor_move_left()
        elif c == "RT":
            self.cursor_move_right()
        elif c == "ES":
            pass
        else:
            self.cache[-1] = self.cache[-1][:self.current_col] + c + self.cache[-1][self.current_col:]
            self.cursor_move_right()
                
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache)
        
    def write_char(self, c):
        if c == "\n":
            self.cache.append(self.prompt_c)
        else:
            self.cache[-1] += c
            if len(self.cache[-1]) > self.display_width_with_prompt:
                self.cache.append(" " + self.cache[-1][self.display_width_with_prompt:])
                self.cache[-2] = self.cache[-2][:display_width_with_prompt]
                
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache) - 1
        self.current_col = len(self.cache[-1])


def main(*args, **kwargs):
    task = args[0]
    name = args[1]
    shell = kwargs["shell"]
    shell_id = kwargs["shell_id"]
    shell.disable_output = True
    try:
        if len(kwargs["args"]) > 0:
            file_path = kwargs["args"][0]
            result = []
            if exists(file_path):
                with open(file_path, "r") as fp:
                    content = fp.read()
                    s = PyShell(display_size = (18, 9))
                    result = s.exec_script(content, args = kwargs["args"][1:])
                shell.disable_output = False
                shell.current_shell = None
                yield Condition(sleep = 0, wait_msg = False, send_msgs = [
                    Message({"output": result}, receiver = shell_id)
                ])
            else:
                raise Exception("file[%s] not exists!" % file_path)
        else:
            s = PyShell(display_size = (18, 9))
            shell.current_shell = s
            s.write_line("   Welcome to Python")
            s.write_char("\n")
            yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                Message({"frame": s.get_display_frame(), "cursor": s.get_cursor_position(1)}, receiver = shell_id)
            ])
            msg = task.get_message()
            c = msg.content["msg"]
            while c != "" and not s.exit:
                #print("char:", c)
                s.input_char(c)
                if not s.exit:
                    yield Condition(sleep = 0, wait_msg = True, send_msgs = [
                        Message({"frame": s.get_display_frame(), "cursor": s.get_cursor_position(1)}, receiver = shell_id)
                    ])
                    msg = task.get_message()
                    c = msg.content["msg"]
            #print("password:", password)
            shell.disable_output = False
            shell.current_shell = None
            yield Condition(sleep = 0, wait_msg = False, send_msgs = [
                Message({"output": "quit from python"}, receiver = shell_id)
            ])
    except Exception as e:
        shell.disable_output = False
        shell.current_shell = None
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": str(e)}, receiver = shell_id)
        ])
