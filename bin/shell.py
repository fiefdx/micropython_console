from scheduler import Condition, Task, Message

class Shell(object):
    def __init__(self, display_size = (20, 8), cache_size = (-1, 30), history_length = 50, prompt_c = ">", scheduler = None, display_id = None, storage_id = None):
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
        
    def get_display_frame(self):
        return self.cache[-self.display_height:]
    
    def set_cursor_color(self, c):
        self.cursor_color = c
    
    def get_cursor_position(self, c = None):
        return self.current_col, self.current_row if self.current_row <= (self.display_height - 1) else (self.display_height - 1), self.cursor_color if c is None else c
    
    def write_char(self, c):
        if c == "\n":
            self.history.append(self.cache[-1][1:])
            self.cache.append(">")
        else:
            self.cache[-1] += c
            if len(self.cache[-1]) > self.display_width + 1:
                self.cache.append(" " + self.cache[-1][self.display_width + 1:])
                self.cache[-2] = self.cache[-2][:self.display_width + 1]
                
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache) - 1
        self.current_col = len(self.cache[-1])
        if len(self.history) > self.history_length:
            self.history.pop(0)
    
    def input_char(self, c):
        if c == "\n":
            self.history.append(self.cache[-1][1:])
            cmd = self.cache[-1][1:].strip()
            self.scheduler.add_task(Task(self.run, cmd, kwargs = {})) # execute cmd
        else:
            self.cache[-1] += c
            if len(self.cache[-1]) > self.display_width + 1:
                self.cache.append(" " + self.cache[-1][self.display_width + 1:])
                self.cache[-2] = self.cache[-2][:self.display_width + 1]
                
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache) - 1
        self.current_col = len(self.cache[-1])
        if len(self.history) > self.history_length:
            self.history.pop(0)
            
    def write_line(self, line):
        self.cache.append(line)
        if len(self.cache) > self.cache_lines:
            self.cache.pop(0)
        self.current_row = len(self.cache) - 1
        self.current_col = len(self.cache[-1])
    
    def write_lines(self, lines):
        lines = lines.split("\n")
        for line in lines:
            self.cache.append(line)
            if len(self.cache) > self.cache_lines:
                self.cache.pop(0)
            self.current_row = len(self.cache) - 1
            self.current_col = len(self.cache[-1])
            
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
            
    def run(self, task, cmd):
        yield Condition(sleep = 0, send_msgs = [
            Message({"cmd": cmd}, receiver = self.storage_id)
        ])
    
    def cursor_move_left(self):
        pass
    
    def cursor_move_right(self):
        pass
    
    def history_previous(self):
        pass
    
    def history_next(self):
        pass
        
    
        