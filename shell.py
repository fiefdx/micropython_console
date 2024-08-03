import uos
from math import ceil

from scheduler import Condition, Task, Message
from common import exists, path_join, isfile, isdir


class Shell(object):
    def __init__(self, display_size = (20, 8), cache_size = (-1, 30), history_length = 100, prompt_c = ">", scheduler = None, display_id = None, storage_id = None, history_file_path = "/.history", bin_path = "/bin"):
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
        self.cursor_id = None
        self.history_idx = 0
        self.scroll_row = 0
        self.frame_history = []
        self.session_task_id = None
        self.disable_output = False
        self.current_shell = None
        self.enable_cursor = True
        self.history_file_path = history_file_path
        self.bin_path = bin_path
        self.load_history()
        from bin import ls, pwd, cd, mkdir, cp, rm, touch, echo, cat, ifconfig, connect, disconnect, reconnect, scan, read, help
        from bin import top, python, clear, learn, reset, edit, editold, readpages, rename, bricks, tank, badapple, umount, mount
    
    def load_history(self):
        if exists(self.history_file_path):
            history_file = open(self.history_file_path, "r")
            history_lines = 0
            line = history_file.readline()
            while line:
                line = line.strip()
                self.history.append(line)
                if len(self.history) > self.history_length:
                    self.history.pop(0)
                history_lines += 1
                line = history_file.readline()
            history_file.close()
            if history_lines > self.history_length:
                tmp_file_path = self.history_file_path + ".tmp"
                if exists(tmp_file_path):
                    uos.remove(tmp_file_path)
                uos.rename(self.history_file_path, tmp_file_path)
                tmp_file = open(tmp_file_path, "r")
                history_file = open(self.history_file_path, "w")
                l = 0
                line = tmp_file.readline()
                while line:
                    l += 1
                    if l > (history_lines - self.history_length):
                        history_file.write(line)
                    line = tmp_file.readline()
                tmp_file.close()
                history_file.close()
                uos.remove(tmp_file_path)
        self.history_file = open(self.history_file_path, "a")
        self.history_idx = len(self.history)
        
    def write_history(self, line):
        if line[-1] != "\n":
            line += "\n"
        self.history_file.write(line)
        self.history_file.flush()
    
    def help_commands(self):
        return "ls\npwd\ncd\nmkdir\nrm\ncp\ntouch\necho\ncat\nifconfig\nconnect\ndisconnect\nreconnect\nscan\nread\ntop\npython\nclear\nlearn\nreset\nedit\neditold\nrename\nbricks\ntank\nbadapple\numount\nmount\nhelp"
        
    def get_display_frame(self):
        # return self.cache[-self.display_height:]
        return self.cache_to_frame()
    
    def cache_to_frame_history(self):
        self.frame_history.clear()
        for n, line in enumerate(self.cache[:-1]):
            for i in range(ceil(len(line) / self.display_width_with_prompt)):
                self.frame_history.append(line[i*self.display_width_with_prompt:(i+1)*self.display_width_with_prompt])
                
    def history_to_frame(self, last_lines, scroll_row):
        frame = []
        total_lines = len(self.frame_history) + len(last_lines)
        end_idx = total_lines + scroll_row - 1
        start_idx = total_lines + scroll_row - self.display_height
        if start_idx < 0:
            start_idx = 0
            end_idx = start_idx + self.display_height - 1
            self.scroll_row = self.display_height - total_lines
        if end_idx >= total_lines:
            end_idx = total_lines - 1
        if start_idx >= 0 and start_idx < len(self.frame_history):
            if end_idx >= 0 and end_idx < len(self.frame_history):
                for i in range(start_idx, end_idx + 1):
                    frame.append(self.frame_history[i])
            else:
                for i in range(start_idx, len(self.frame_history)):
                    frame.append(self.frame_history[i])
                for i in range(0, end_idx - len(self.frame_history) + 1):
                    frame.append(last_lines[i])
        else:
            for i in range(start_idx - len(self.frame_history), end_idx - len(self.frame_history) + 1):
                frame.append(last_lines[i])
        return frame
    
    def cache_to_frame(self):
        frame = []
        self.cursor_row = 0
        self.cursor_col = 0
        row = -1
        if self.scroll_row == 0:
            lines = self.cache[-self.display_height:]
            for n, line in enumerate(lines):
                if len(line) > 0:
                    for i in range(ceil(len(line) / self.display_width_with_prompt)):
                        frame.append(line[i*self.display_width_with_prompt:(i+1)*self.display_width_with_prompt])
                        row += 1
                        if len(frame) > self.display_height:
                            frame.pop(0)
                            row -= 1
                        if n == len(lines) - 1: # last line in cache
                            if ceil(self.current_col / self.display_width_with_prompt) == (i + 1): # cursor in current line
                                self.cursor_row = row
                                self.cursor_col = self.current_col % self.display_width_with_prompt
                                if self.cursor_col == 0:
                                    self.cursor_col = 21
                                #print("cursor_row: ", row, "cursor_col: ", self.cursor_col)
                            elif ceil(self.current_col / self.display_width_with_prompt) < (i + 1):
                                if len(frame) >= self.display_height:
                                    self.cursor_row -= 1
                else:
                    frame.append(line)
                    row += 1
        else:
            frame_lines = []
            line = self.cache[-1]
            for i in range(ceil(len(line) / self.display_width_with_prompt)):
                frame_lines.append(line[i*self.display_width_with_prompt:(i+1)*self.display_width_with_prompt])
            frame = self.history_to_frame(frame_lines, self.scroll_row)
        return frame
        
    def get_cursor_position(self, c = None):
        #print("get_cursor_position:", self.cursor_col, self.cursor_row)
        if self.current_shell:
            return self.current_shell.get_cursor_position(c)
        if self.enable_cursor:
            return self.cursor_col, self.cursor_row, self.cursor_color if c is None else c
        else:
            return self.cursor_col, self.cursor_row, 0
    
    def set_cursor_position(self, col, row):
        #print("set_cursor_position:", col, row)
        self.cursor_col, self.cursor_row = col, row
    
    def set_cursor_color(self, c):
        if self.current_shell:
            self.current_shell.set_cursor_color(c)
        self.cursor_color = c
    
    def get_cursor_cache_position(self, c = None):
        return self.current_col, self.current_row if self.current_row <= (self.display_height - 1) else (self.display_height - 1), self.cursor_color if c is None else c
    
    def write_char(self, c):
        if c == "\n":
            self.cache.append(self.prompt_c)
        else:
            self.cache[-1] += c
            if len(self.cache[-1]) > self.display_width_with_prompt:
                self.cache.append(" " + self.cache[-1][self.display_width_with_prompt:])
                self.cache[-2] = self.cache[-2][:self.display_width_with_prompt]
                
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache) - 1
        self.current_col = len(self.cache[-1])
    
    def input_char(self, c):
        if self.session_task_id is not None and self.scheduler.exists_task(self.session_task_id):
            self.scheduler.add_task(Task(self.send_session_message, c, kwargs = {})) # execute cmd
        else:
            if c == "\n":
                cmd = self.cache[-1][len(self.prompt_c):].strip()
                if len(cmd) > 0:
                    if self.session_task_id is not None and self.scheduler.exists_task(self.session_task_id):
                        self.scheduler.add_task(Task(self.send_session_message, self.cache[-1].strip(), kwargs = {})) # execute cmd
                    else:
                        self.history.append(self.cache[-1][len(self.prompt_c):])
                        self.write_history(self.cache[-1][len(self.prompt_c):])
                        command = cmd.split(" ")[0].strip()
                        if command in ("connect", "cat", "scan", "reconnect", "read", "help", "top", "python", "learn", "reset", "edit", "readpages", "editold", "cp", "rm", "bricks", "tank", "badapple"):
                            self.scheduler.add_task(Task(self.run_coroutine, cmd, kwargs = {})) # execute cmd
                        else:
                            self.scheduler.add_task(Task(self.run, cmd, kwargs = {})) # execute cmd
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
            elif c in ("ES", "SAVE"):
                pass
            else:
                self.cache[-1] = self.cache[-1][:self.current_col] + c + self.cache[-1][self.current_col:]
                self.cursor_move_right()
                
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache)
        #self.current_col = len(self.cache[-1])
            
    def write_line(self, line):
        self.cache.append(line)
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache) - 1
        self.current_col = len(self.cache[-1])
        self.cache_to_frame_history()
    
    def write_lines(self, lines, end = False):
        lines = lines.split("\n")
        for line in lines:
            #if len(line) > 0:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            self.cache.append(line)
            if len(self.cache) > self.cache_lines:
                self.cache.pop(0)
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])
        if end:
            self.write_char("\n")
        self.cache_to_frame_history()
            
    def write(self, s):
        line_width = self.display_width_with_prompt
        d = s[:line_width]
        s = s[line_width:]
        while len(d) > 0:
            self.cache.append(d)
            if len(self.cache) > self.cache_lines:
                self.cache.pop(0)
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])
            d = s[:line_width]
            s = s[line_width:]
        self.write_char("\n")
        self.cache_to_frame_history()
            
    def run(self, task, cmd):
        yield Condition(sleep = 0, send_msgs = [
            Message({"cmd": cmd}, receiver = self.storage_id)
        ])
        
    def send_session_message(self, task, msg):
        #print("send_session_message:", msg, self.session_task_id)
        yield Condition(sleep = 0, send_msgs = [
            Message({"msg": msg}, receiver = self.session_task_id)
        ])
        
    def run_coroutine(self, task, cmd):
        #print("run_coroutine: ", task, cmd)
        import bin
        args = cmd.split(" ")
        module = args[0].split(".")[0]
        #if "/sd/usr" not in sys.path:
        #    sys.path.insert(0, "/sd/usr")
        #import bin
        import_str = "from bin import %s" % module
        exec(import_str)
        self.session_task_id = self.scheduler.add_task(Task(bin.__dict__[module].main, cmd, kwargs = {"args": args[1:], "shell_id": self.scheduler.shell_id, "shell": self})) # execute cmd
    
    def cursor_move_left(self):
        if self.current_col > len(self.prompt_c):
            self.current_col -= 1
        #print("current_col: ", self.current_col)
    
    def cursor_move_right(self):
        if self.current_col < len(self.cache[-1]):
            self.current_col += 1
        #print("current_col: ", self.current_col)
        
    def scroll_up(self):
        self.scroll_row -= 1
        #print("scroll_row:", self.scroll_row)
        
    def scroll_down(self):
        self.scroll_row += 1
        if self.scroll_row >= 0:
            self.scroll_row = 0
        #print("scroll_row:", self.scroll_row)
    
    def history_previous(self):
        self.history_idx -= 1
        if self.history_idx <= 0:
            self.history_idx = 0
        #print("history:", self.history, self.history_idx)
        if len(self.history) > 0:
            #if self.history_idx > len(self.history) - 1:
            #    self.history_idx = len(self.history) - 1
            #print("history:", self.history, self.history_idx)
            self.cache[-1] = self.prompt_c + self.history[self.history_idx]
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])
        
    def history_next(self):
        self.history_idx += 1
        if self.history_idx > len(self.history) - 1:
            self.history_idx = len(self.history)
        #print("history:", self.history, self.history_idx)
        if len(self.history) > 0:
            if self.history_idx > len(self.history) - 1:
                self.cache[-1] = self.prompt_c
            else:
                self.cache[-1] = self.prompt_c + self.history[self.history_idx]
            #print("history:", self.history, self.history_idx)
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])


class ShellOld(object):
    def __init__(self, display_size = (20, 8), cache_size = (-1, 30), history_length = 100, prompt_c = ">", scheduler = None, display_id = None, storage_id = None, history_file_path = "/sd/.history", bin_path = "/bin"):
        self.display_width = display_size[0]
        self.display_height = display_size[1]
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
        self.disable_output = False
        self.current_shell = None
        self.enable_cursor = True
        self.history_file_path = history_file_path
        self.bin_path = bin_path
        self.load_history()
        from bin import ls, pwd, cd, mkdir, rm, touch, echo, cat, ifconfig, connect, disconnect, reconnect, scan, read, help, top, python, clear, learn
    
    def load_history(self):
        if exists(self.history_file_path):
            history_file = open(self.history_file_path, "r")
            history_lines = 0
            line = history_file.readline()
            while line:
                line = line.strip()
                self.history.append(line)
                if len(self.history) > self.history_length:
                    self.history.pop(0)
                history_lines += 1
                line = history_file.readline()
            history_file.close()
            if history_lines > self.history_length:
                tmp_file_path = self.history_file_path + ".tmp"
                if exists(tmp_file_path):
                    uos.remove(tmp_file_path)
                uos.rename(self.history_file_path, tmp_file_path)
                tmp_file = open(tmp_file_path, "r")
                history_file = open(self.history_file_path, "w")
                l = 0
                line = tmp_file.readline()
                while line:
                    l += 1
                    if l > (history_lines - self.history_length):
                        history_file.write(line)
                    line = tmp_file.readline()
                tmp_file.close()
                history_file.close()
                uos.remove(tmp_file_path)
        self.history_file = open(self.history_file_path, "a")
        self.history_idx = len(self.history)
        
    def write_history(self, line):
        if line[-1] != "\n":
            line += "\n"
        self.history_file.write(line)
        self.history_file.flush()
    
    def help_commands(self):
        return "ls\npwd\ncd\nmkdir\nrm\ntouch\necho\ncat\nifconfig\nconnect\ndisconnect\nreconnect\nscan\nread\ntop\npython\nclear\nlearn\nhelp"
        
    def get_display_frame(self):
        # return self.cache[-self.display_height:]
        return self.cache_to_frame()
    
    def cache_to_frame_history(self):
        self.frame_history.clear()
        for n, line in enumerate(self.cache[:-1]):
            for i in range(ceil(len(line) / (self.display_width + 1))):
                self.frame_history.append(line[i*(self.display_width + 1):(i+1)*(self.display_width + 1)])
                
    def history_to_frame(self, last_lines, scroll_row):
        frame = []
        total_lines = len(self.frame_history) + len(last_lines)
        end_idx = total_lines + scroll_row - 1
        start_idx = total_lines + scroll_row - self.display_height
        if start_idx < 0:
            start_idx = 0
            end_idx = start_idx + self.display_height - 1
            self.scroll_row = self.display_height - total_lines
        if end_idx >= total_lines:
            end_idx = total_lines - 1
        if start_idx >= 0 and start_idx < len(self.frame_history):
            if end_idx >= 0 and end_idx < len(self.frame_history):
                for i in range(start_idx, end_idx + 1):
                    frame.append(self.frame_history[i])
            else:
                for i in range(start_idx, len(self.frame_history)):
                    frame.append(self.frame_history[i])
                for i in range(0, end_idx - len(self.frame_history) + 1):
                    frame.append(last_lines[i])
        else:
            for i in range(start_idx - len(self.frame_history), end_idx - len(self.frame_history) + 1):
                frame.append(last_lines[i])
        return frame
    
    def cache_to_frame(self):
        frame = []
        self.cursor_row = 0
        self.cursor_col = 0
        row = -1
        if self.scroll_row == 0:
            lines = self.cache[-self.display_height:]
            for n, line in enumerate(lines):
                if len(line) > 0:
                    for i in range(ceil(len(line) / (self.display_width + 1))):
                        frame.append(line[i*(self.display_width + 1):(i+1)*(self.display_width + 1)])
                        row += 1
                        if len(frame) > self.display_height:
                            frame.pop(0)
                            row -= 1
                        if n == len(lines) - 1: # last line in cache
                            if ceil(self.current_col / (self.display_width + 1)) == (i + 1): # cursor in current line
                                self.cursor_row = row
                                self.cursor_col = self.current_col % (self.display_width + 1)
                                if self.cursor_col == 0:
                                    self.cursor_col = 21
                                #print("cursor_row: ", row, "cursor_col: ", self.cursor_col)
                            elif ceil(self.current_col / (self.display_width + 1)) < (i + 1):
                                if len(frame) >= self.display_height:
                                    self.cursor_row -= 1
                else:
                    frame.append(line)
                    row += 1
        else:
            frame_lines = []
            line = self.cache[-1]
            for i in range(ceil(len(line) / (self.display_width + 1))):
                frame_lines.append(line[i*(self.display_width + 1):(i+1)*(self.display_width + 1)])
            frame = self.history_to_frame(frame_lines, self.scroll_row)
        return frame
        
    def get_cursor_position(self, c = None):
        #print("get_cursor_position:", self.cursor_col, self.cursor_row)
        if self.current_shell:
            return self.current_shell.get_cursor_position(c)
        return self.cursor_col, self.cursor_row, self.cursor_color if c is None else c
    
    def set_cursor_position(self, col, row):
        #print("set_cursor_position:", col, row)
        self.cursor_col, self.cursor_row = col, row
    
    def set_cursor_color(self, c):
        if self.current_shell:
            self.current_shell.set_cursor_color(c)
        self.cursor_color = c
    
    def get_cursor_cache_position(self, c = None):
        return self.current_col, self.current_row if self.current_row <= (self.display_height - 1) else (self.display_height - 1), self.cursor_color if c is None else c
    
    def write_char(self, c):
        if c == "\n":
            self.cache.append(self.prompt_c)
        else:
            self.cache[-1] += c
            if len(self.cache[-1]) > self.display_width + 1:
                self.cache.append(" " + self.cache[-1][self.display_width + 1:])
                self.cache[-2] = self.cache[-2][:self.display_width + 1]
                
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache) - 1
        self.current_col = len(self.cache[-1])
    
    def input_char(self, c):
        if self.session_task_id is not None and self.scheduler.exists_task(self.session_task_id):
            self.scheduler.add_task(Task(self.send_session_message, c, kwargs = {})) # execute cmd
        else:
            if c == "\n":
                cmd = self.cache[-1][len(self.prompt_c):].strip()
                if len(cmd) > 0:
                    if self.session_task_id is not None and self.scheduler.exists_task(self.session_task_id):
                        self.scheduler.add_task(Task(self.send_session_message, self.cache[-1].strip(), kwargs = {})) # execute cmd
                    else:
                        self.history.append(self.cache[-1][len(self.prompt_c):])
                        self.write_history(self.cache[-1][len(self.prompt_c):])
                        command = cmd.split(" ")[0].strip()
                        if command in ("connect", "cat", "scan", "reconnect", "read", "help", "top", "python", "learn"):
                            self.scheduler.add_task(Task(self.run_coroutine, cmd, kwargs = {})) # execute cmd
                        else:
                            self.scheduler.add_task(Task(self.run, cmd, kwargs = {})) # execute cmd
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
        #self.current_col = len(self.cache[-1])
            
    def write_line(self, line):
        self.cache.append(line)
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache) - 1
        self.current_col = len(self.cache[-1])
        self.cache_to_frame_history()
    
    def write_lines(self, lines, end = False):
        lines = lines.split("\n")
        for line in lines:
            #if len(line) > 0:
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            self.cache.append(line)
            if len(self.cache) > self.cache_lines:
                self.cache.pop(0)
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])
        if end:
            self.write_char("\n")
        self.cache_to_frame_history()
            
    def write(self, s):
        line_width = self.display_width + 1
        d = s[:line_width]
        s = s[line_width:]
        while len(d) > 0:
            self.cache.append(d)
            if len(self.cache) > self.cache_lines:
                self.cache.pop(0)
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])
            d = s[:line_width]
            s = s[line_width:]
        self.write_char("\n")
        self.cache_to_frame_history()
            
    def run(self, task, cmd):
        yield Condition(sleep = 0, send_msgs = [
            Message({"cmd": cmd}, receiver = self.storage_id)
        ])
        
    def send_session_message(self, task, msg):
        #print("send_session_message:", msg, self.session_task_id)
        yield Condition(sleep = 0, send_msgs = [
            Message({"msg": msg}, receiver = self.session_task_id)
        ])
        
    def run_coroutine(self, task, cmd):
        #print("run_coroutine: ", task, cmd)
        import bin
        args = cmd.split(" ")
        module = args[0].split(".")[0]
        #if "/sd/usr" not in sys.path:
        #    sys.path.insert(0, "/sd/usr")
        #import bin
        import_str = "from bin import %s" % module
        exec(import_str)
        self.session_task_id = self.scheduler.add_task(Task(bin.__dict__[module].main, cmd, kwargs = {"args": args[len(self.prompt_c):], "shell_id": self.scheduler.shell_id, "shell": self})) # execute cmd
    
    def cursor_move_left(self):
        if self.current_col > len(self.prompt_c):
            self.current_col -= 1
        #print("current_col: ", self.current_col)
    
    def cursor_move_right(self):
        if self.current_col < len(self.cache[-1]):
            self.current_col += 1
        #print("current_col: ", self.current_col)
        
    def scroll_up(self):
        self.scroll_row -= 1
        #print("scroll_row:", self.scroll_row)
        
    def scroll_down(self):
        self.scroll_row += 1
        if self.scroll_row >= 0:
            self.scroll_row = 0
        #print("scroll_row:", self.scroll_row)
    
    def history_previous(self):
        self.history_idx -= 1
        if self.history_idx <= 0:
            self.history_idx = 0
        #print("history:", self.history, self.history_idx)
        if len(self.history) > 0:
            #if self.history_idx > len(self.history) - 1:
            #    self.history_idx = len(self.history) - 1
            #print("history:", self.history, self.history_idx)
            self.cache[-1] = self.prompt_c + self.history[self.history_idx]
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])
            
        
    def history_next(self):
        self.history_idx += 1
        if self.history_idx > len(self.history) - 1:
            self.history_idx = len(self.history)
        #print("history:", self.history, self.history_idx)
        if len(self.history) > 0:
            if self.history_idx > len(self.history) - 1:
                self.cache[-1] = self.prompt_c
            else:
                self.cache[-1] = self.prompt_c + self.history[self.history_idx]
            #print("history:", self.history, self.history_idx)
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])
        