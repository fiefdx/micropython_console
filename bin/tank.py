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

class Bullet(object):
    def __init__(self, speed):
        self.x = None
        self.y = None
        self.direction = None
        self.speed = speed
        self.frames = 0
        self.fired = False
        
    def fire(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.fired = True
        
    def update(self, width, height):
        self.frames += 1
        if self.fired and self.frames >= self.speed:
            self.frames = 0
            if self.direction == "up":
                self.y -= 1
                if self.y < 0:
                    self.fired = False
            elif self.direction == "down":
                self.y += 1
                if self.y > height - 1:
                    self.fired = False
            elif self.direction == "left":
                self.x -= 1
                if self.x < 0:
                    self.fired = False
            elif self.direction == "right":
                self.x += 1
                if self.x > width - 1:
                    self.fired = False
                
                
class Tank(object):
    def __init__(self, speed, bullets, bullet_speed):
        self.x = None
        self.y = None
        self.direction = None
        self.speed = speed
        self.frames = 0
        self.bullet_speed = bullet_speed
        self.bullets = [Bullet(bullet_speed) for i in range(bullets)]
        self.live = False
        
    def set_live(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.live = True
        
    def fire_ready(self):
        for b in self.bullets:
            if not b.fired:
                return True
        return False
    
    def fire(self):
        for b in self.bullets:
            if not b.fired:
                b.fire(self.x, self.y, self.direction)
                
    def update_bullets(self, width, height):
        for b in self.bullets:
            b.update(width, height)
        
    def update(self, width, height):
        self.frames += 1
        if self.frames >= self.speed:
            self.frames = 0
            next_step = "forward"
            if self.fire_ready():
                next_step = random.choice(["forward", "forward", "forward", "turn", "fire"])
            else:
                next_step = random.choice(["forward", "forward", "forward", "turn"])
            if next_step == "forward":
                if self.direction == "up":
                    if self.y > 1:
                        self.y -= 1
                elif self.direction == "down":
                    if self.y < height - 2:
                        self.y += 1
                elif self.direction == "left":
                    if self.x > 1:
                        self.x -= 1
                elif self.direction == "right":
                    if self.x < width - 2:
                        self.x += 1
            elif next_step == "turn":
                directions = ["up", "left", "right", "down"]
                directions.remove(self.direction)
                self.direction = random.choice(directions)
            else:
                self.fire()
        self.update_bullets(width, height)


class World(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.frame_p = None
        self.frame_c = self.clear_frame()
        self.tanks = []
        
    def clear_frame(self):
        data = []
        for h in range(self.height):
            data.append([])
            for w in range(self.width):
                data[h].append(False)
        return data
        
    def have_space(self, x, y):
        return any(self.frame_c[y-1][x-1:x+2]) is False and any(self.frame_c[y][x-1:x+2]) is False and any(self.frame_c[y+1][x-1:x+2]) is False
        
    def place_tank(self, tank):
        directions = ["up", "left", "right", "down"]
        direction = random.choice(directions)
        positions = []
        if self.have_space(1, 1):
            positions.append((1, 1))
        if self.have_space(self.width - 2, 1):
            positions.append((self.width - 2, 1))
        if positions:
            x, y = random.choice(positions)
            tank.set_live(x, y, direction)
            
    def draw_tank(self, tank):
        if tank.direction == "up":
            self.frame_c[tank.y-1][tank.x] = True
            self.frame_c[tank.y][tank.x] = True
            self.frame_c[tank.y][tank.x-1] = True
            self.frame_c[tank.y][tank.x+1] = True
            self.frame_c[tank.y+1][tank.x-1] = True
            self.frame_c[tank.y+1][tank.x+1] = True
        elif tank.direction == "down":
            self.frame_c[tank.y+1][tank.x] = True
            self.frame_c[tank.y][tank.x] = True
            self.frame_c[tank.y][tank.x-1] = True
            self.frame_c[tank.y][tank.x+1] = True
            self.frame_c[tank.y-1][tank.x-1] = True
            self.frame_c[tank.y-1][tank.x+1] = True
        elif tank.direction == "left":
            self.frame_c[tank.y][tank.x-1] = True
            self.frame_c[tank.y][tank.x] = True
            self.frame_c[tank.y+1][tank.x] = True
            self.frame_c[tank.y-1][tank.x] = True
            self.frame_c[tank.y+1][tank.x+1] = True
            self.frame_c[tank.y-1][tank.x+1] = True
        elif tank.direction == "right":
            self.frame_c[tank.y][tank.x+1] = True
            self.frame_c[tank.y][tank.x] = True
            self.frame_c[tank.y+1][tank.x] = True
            self.frame_c[tank.y-1][tank.x] = True
            self.frame_c[tank.y+1][tank.x-1] = True
            self.frame_c[tank.y-1][tank.x-1] = True
        for b in tank.bullets:
            if b.fired:
                self.frame_c[b.y][b.x] = True
        
    def update(self):
        self.frame_p = self.frame_c
        self.frame_c = self.clear_frame()
        for t in self.tanks:
            if not t.live:
                self.place_tank(t)
            if t.live:
                t.update(self.width, self.height)
                self.draw_tank(t)
                
    def get_diff_frame(self):
        frame = self.clear_frame()
        for y in range(self.height):
            for x in range(self.width):
                if self.frame_c[y][x] != self.frame_p[y][x]:
                    frame[y][x] = "x" if self.frame_c[y][x] else "o"
        return frame


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
        if len(kwargs["args"]) > 3:
            width = int(kwargs["args"][0])
            height = int(kwargs["args"][1])
            size = int(kwargs["args"][2])
            frame_interval = int(kwargs["args"][3])
            yield Condition(sleep = 0, send_msgs = [
                Message({"clear": True}, receiver = display_id)
            ])
            yield Condition(sleep = 0, send_msgs = [
                Message({"enabled": False}, receiver = cursor_id)
            ])
            w = World(width, height)
            w.tanks.append(Tank(5, 1, 3))
            w.tanks.append(Tank(2, 1, 1))
            w.tanks.append(Tank(1, 1, 1))
            w.tanks.append(Tank(0, 1, 0))
            w.update()
            yield Condition(sleep = frame_interval, wait_msg = False, send_msgs = [
                Message({"bricks": {"data": w.get_diff_frame(), "width": width, "height": height, "size": size}}, receiver = display_id)
            ])
            c = None
            msg = task.get_message()
            if msg:
                c = msg.content["msg"]
            while c != "ES":
                w.update()
                yield Condition(sleep = frame_interval, wait_msg = False, send_msgs = [
                    Message({"bricks": {"data": w.get_diff_frame(), "width": width, "height": height, "size": size}}, receiver = display_id)
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
        


