import gc
import sys

from ina219 import INA219
from scheduler import Condition, Message

def main(*args, **kwargs):
    task = args[0]
    name = args[1]
    result = "invalid parameters"
    shell_id = kwargs["shell_id"]
    shell = kwargs["shell"]
    shell.enable_cursor = False
    width, height = 21, 9
    try:
        app_exit = False
        ina219 = INA219(addr=0x43)
        while not app_exit:
            frame = []
            gc.collect()
            monitor_msg = " CPU%s:%3d%%  RAM:%3d%%" % (shell.scheduler.cpu, int(100 - shell.scheduler.idle), int(100 - (shell.scheduler.mem_free() * 100 / (264 * 1024))))
            frame.append(monitor_msg)
            bus_voltage = ina219.getBusVoltage_V()             # voltage on V- (load side)
            current = ina219.getCurrent_mA()/1000              # current in A
            P = (bus_voltage -3)/1.2*100
            if(P<0):P=0
            elif(P>100):P=100
            battery_msg = " %5.3fV %6.3fA %3d%%" % (bus_voltage, current, P)
            frame.append(battery_msg)
            for i, t in enumerate(shell.scheduler.tasks):
                frame.append("%03d %17s"  % (t.id, t.name))
            for i in range(0, height - len(frame)):
                frame.append("")
            yield Condition(sleep = 1000, wait_msg = False, send_msgs = [
                Message({"output_part": "\n".join(frame[:height])}, receiver = shell_id)
            ])
            yield Condition(sleep = 1000)
            msg = task.get_message()
            if msg and msg.content["msg"] == "ES":
                app_exit = True
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": ""}, receiver = shell_id)
        ])
        shell.enable_cursor = True
    except Exception as e:
        yield Condition(sleep = 0, send_msgs = [
            Message({"output": sys.print_exception(e)}, receiver = shell_id)
        ])
        shell.enable_cursor = True
