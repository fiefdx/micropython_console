import gc
import sys

from common import ticks_ms, ticks_add, ticks_diff, sleep_ms


class Message(object):
    def __init__(self, content, sender = None, sender_name = "", receiver = None):
        self.content = content
        self.sender = sender
        self.sender_name = sender_name
        self.receiver = receiver


class Condition(object):
    def __init__(self, code = 0, sleep = 0, send_msgs = [], wait_msg = False):
        self.code = code
        self.resume_at = ticks_add(ticks_ms(), sleep) # ms
        self.send_msgs = send_msgs
        self.wait_msg = wait_msg
        
        
class Task(object):
    id_count = 0
    
    @classmethod
    def new_id(cls):
        cls.id_count += 1
        return cls.id_count
    
    def __init__(self, func, name, condition = Condition(), task_id = None, args = [], kwargs = {}):
        self.id = Task.new_id()
        if task_id:
            self.id = task_id
        self.name = name
        self.msgs = []
        self.msgs_senders = []
        self.func = func(self, name, *args, **kwargs)
        self.condition = condition
        
    def set_condition(self, condition):
        self.condition = condition
        
    def put_message(self, message):
        self.msgs.append(message)
        self.msgs_senders.append(message.sender)
        
    def get_message(self, sender = None):
        msg = None
        try:
            if sender is None:
                msg = self.msgs.pop(0)
                _ = self.msgs_senders.pop(0)
            else:
                i = self.msgs_senders.index(sender)
                msg = self.msgs.pop(i)
                _ = self.msgs_senders.pop(i)
        except Exception as e:
            pass
        return msg
        
    def ready(self):
        if ticks_diff(ticks_ms(), self.condition.resume_at) >= 0:
            if self.condition.wait_msg is True:
                return len(self.msgs) > 0
            elif self.condition.wait_msg >= 1:
                return self.condition.wait_msg in self.msgs_senders
            else:
                return True
        else:
            return False


class Scheluder(object):
    def __init__(self, log_to = None, name = "scheduler", cpu = 0):
        self.log_to = log_to
        self.cpu = cpu
        self.name = name
        self.tasks = []
        self.tasks_ids = {}
        self.task_sort_at = 0
        self.current = None
        self.sleep_ms = 0
        self.load_calc_at = ticks_ms()
        self.idle = 0
        self.idle_sleep_interval = 0.1
        self.task_sleep_interval = 0.1
        self.need_to_sort = True
        self.stop = False
        
    def task_sort(self, task):
        if task.condition.wait_msg:
            if len(task.msgs) > 0:
                return -1000000
            else:
                return 1000000
        return ticks_diff(task.condition.resume_at, self.task_sort_at)

    def add_task(self, task, condition = None):
        self.tasks.append(task)
        self.tasks_ids[task.id] = task
        return task.id

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
        del self.tasks_ids[task.id]
        
    def exists_task(self, task_id):
        return task_id in self.tasks_ids
        
    def send_msg(self, msg):
        self.msgs.put(msg)
        
    def mem_free(self):
        return gc.mem_free()
    
    def cpu_idle(self):
        return self.idle
    
    def set_log_to(self, task_id):
        self.log_to = task_id
    
    def log(self, content):
        if self.log_to:
            self.tasks_ids[self.log_to].put_message(Message(content, sender = 0, sender_name = self.name))
        else:
            print(content)

    def run(self):
        while not self.stop:
            try:
                load_interval = ticks_diff(ticks_ms(), self.load_calc_at)
                if load_interval >= 1000:
                    self.idle = self.sleep_ms * 100 / load_interval
                    if self.idle > 100:
                        self.idle = 100
                    self.sleep_ms = 0
                    self.load_calc_at = ticks_ms()
                if self.tasks:
                    #print(self.tasks)
                    if self.need_to_sort == True:
                        self.task_sort_at = ticks_ms()
                        self.tasks.sort(key = self.task_sort)
                        self.need_to_sort = False
                    if self.current is None:
                        peek = self.tasks[0]
                        now = ticks_ms()
                        if peek.ready():
                            # print("ready: %s" % peek.id)
                            self.current = self.tasks.pop(0)
                            try:
                                self.current.set_condition(next(self.current.func))
                                self.tasks.append(self.current)
                                for msg in self.current.condition.send_msgs:
                                    msg.sender = self.current.id
                                    msg.sender_name = self.current.name
                                    if msg.receiver in self.tasks_ids:
                                        self.tasks_ids[msg.receiver].put_message(msg)
                                self.current = None
                                self.need_to_sort = True
                            except StopIteration:
                                self.remove_task(self.current)
                                self.current = None
                            except TypeError:
                                self.current = None
                            except Exception as e:
                                self.log("task: %s: %s" % (self.current.name, sys.print_exception(e)))
                                self.current = None
                        else:
                            sleep_ms(self.task_sleep_interval)
                            self.sleep_ms += self.task_sleep_interval
                else:
                    sleep_ms(self.idle_sleep_interval)
                    self.sleep_ms += self.idle_sleep_interval
            except KeyboardInterrupt as e:
                self.log("scheduler exit: %s" % sys.print_exception(e))
                break
            except Exception as e:
                self.log("scheduler exit: %s" % sys.print_exception(e))

