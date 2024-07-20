#Micro Python UC1609 192*64 lcd driver
from micropython import const
import framebuf

MTP_CTRL   =const(0xF8)#follows with 0xD0 to disable MTP ok
TEMP_COMP  =const(0x24)# ok
FRAMERATE  =const(0xA0)#|0x01:95fps(default) 00:76fps 02:132fps 03:168fps ok
SET_CAL    =const(0x00)#ca[3:0] ok
SET_CAH    =const(0x10)#ca[7:4] ok
SET_PA     =const(0xB0)#pa[3:0]  ok
ADDR_CTRL  =const(0x89)#MONO_VLSB ok
INV_DISP   =const(0xA6)#|self.INV ok
MAP_CTRL   =const(0xC0)#|self.MAP ok

PARDISPCTRL=const(0x84)#|0x00 to disable Partial display ok
BIAS_RATIO =const(0xE8)#|self.BR ok
POTE_METER =const(0x81)#follows with self.PM ok
POWER_CTRL =const(0x2C)#|0x02:1.4ma 00:0.6ma 01:1.0ma 03:2.3ma ok
APO        =const(0xA4)#0x00:disable all pixel on state
DISP_ON    =const(0xAE)#0x01:display on

class UC1609(framebuf.FrameBuffer):
    def __init__(self, spi, dc, cs, rst, potMeter=0xa8, biasRatio=0x03, invX=1, invY=0, invdisp=0):
        self.width = 192
        self.height = 64
        dc.init(dc.OUT,value=0)
        cs.init(cs.OUT,value=1)#disable device port
        rst.init(rst.OUT,value=0)#reset device
        self.dc=dc
        self.cs=cs
        self.rst=rst
        self.spi=spi
        
        self.PM=potMeter#0x00~0xFF
        self.BR=biasRatio#0x03:x9 02:x8 01:x7 00:x6
        self.INV=0x01 if (invdisp!=0) else 0x00
        self.MAP=0x00
        if (invX!=0):
            self.MAP|=0x04
        if (invY!=0):
            self.MAP|=0x02
        self.buffer=bytearray(192*(64//8))
        super().__init__(self.buffer, 192, 64, framebuf.MONO_VLSB)
        self.initscreen()
        
    def initscreen(self):
        import time
        time.sleep_ms(6)
        self.rst.value(1)
        time.sleep_ms(6)#reset done
        for cmd in(
            MTP_CTRL,
            0xD0,#disable MTP
            PARDISPCTRL|0x00,#disable partial display
            TEMP_COMP|0x03,#disable temp comp
            BIAS_RATIO|self.BR,
            POTE_METER,
            self.PM,
            POWER_CTRL|0x02,
            MAP_CTRL|self.MAP,
            INV_DISP|self.INV,
            FRAMERATE|0x01,#95fps
            ADDR_CTRL,
            SET_CAL,
            SET_CAH,
            SET_PA,
            APO|0x00
            ):
            self.writeCMD(cmd)
        self.fill(0)
        self.show()
        self.writeCMD(DISP_ON|0x01)#1:display on normal display mode
        
    def writeCMD(self,cmd):
        self.cs.value(0)#enable device port
        self.dc.value(0)#cmd mode
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)#disable device port 
    
    def writeData(self,data):
        self.cs.value(0)#enable device port
        self.dc.value(1)#display data mode
        self.spi.write(data)
        self.cs.value(1)#disable device port

    def show(self):
        #write_cmd(ADDR_CTRL)
        #self.writeCMD(DISP_ON|0x00)
        self.writeCMD(SET_CAL)
        self.writeCMD(SET_CAH)
        self.writeCMD(SET_PA)
        self.writeData(self.buffer)
        #self.writeCMD(DISP_ON|0x01)