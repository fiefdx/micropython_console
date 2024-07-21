# ST75256 256x128 LCD Driver
import time
import framebuf
from micropython import const


class Base(framebuf.FrameBuffer):
    def __init__(self, width, height, rot=1):
        self.width = width
        self.height = height
        self.rot=rot
        self.buffer = bytearray(self.width * self.height//8)
        if self.rot==0 or self.rot==2:
            super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        else:
            super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HMSB)
        self.init_display()

    def init_display(self):
        
        cmd_list=[
            [0x30,],# extended instructions 1
            [0x94,],# exit sleep mode
            [0x31,],# extended instructions 2
            [0xD7,0X9F],# disable automatic reading
            [0x32,0x00,0x01,0x03],# bias ratio setting
            [0xF2,0x1e,0x28,0x32],# temperature range setting
            [0x20,0x01,0x03,0x05,0x07,0x09,0x0b,0x0d,0x10,0x11,
             0x13,0x15,0x17,0x19,0x1b,0x1d,0x1f], # grayscale control
            [0x30,],# extended instructions 1
            [0xCA,0X00,0X9F,0X20],# display control, cl, duty cycle, frame period
            [0xF0,0X10],# mono color display
            [0x81,0x0a,0x04],# contrast control
            [0x20,0x0B] ]# power control

        for cmd in cmd_list:
            self.write_cmd(cmd)
        if self.rot==0:
            self.write_cmd([0x08,])
            self.write_cmd([0xBC,0X03])
        elif self.rot==1:
            self.write_cmd([0x08,])
            self.write_cmd([0xBC,0X05])
        elif self.rot==2:
            self.write_cmd([0x0C,])
            self.write_cmd([0xBC,0X00])
        else :
            self.write_cmd([0x0C,])
            self.write_cmd([0xBC,0X06])
        self.fill(0)
        self.show()
        self.poweron()

    def poweroff(self):
        self.write_cmd([0xAE,])

    def poweron(self):
        self.write_cmd([0xAF,])

    def contrast(self, contrast = 0x138):
        if contrast<0x200:
            cmd=[0x81,0x0a,0x04]
            cmd[1]=contrast%64
            cmd[2]=contrast//64
            self.write_cmd(cmd)

    def invert(self, invert):
        if invert:
            self.write_cmd([0xA7,])
        else:
            self.write_cmd([0xA6,])

    def show(self):
        self.write_cmd([0x15,0x00,0xff])
        if self.rot == 0 or self.rot == 1:
            self.write_cmd([0x75,0x01,0x10])
        else:
            self.write_cmd([0x75,0x04,0x13])
        self.write_cmd([0x5C,])
        self.write_data(self.buffer)


class ST75256(Base):
    def __init__(self, width, height, spi, dc, res, cs, rot=1):
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        time.sleep_ms(10)
        super().__init__(width, height,rot=rot)
       
    def write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd[0],]))
        self.dc(1)
        if len(cmd)>1:
            self.spi.write(bytearray(cmd[1:]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)