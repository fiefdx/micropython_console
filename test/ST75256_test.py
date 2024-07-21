import os
import gc
import time
import uos
from machine import Pin, SPI

from ST75256 import ST75256
import font7
import font8
from writer import Writer

display_cs = machine.Pin(5, machine.Pin.OUT)
spi = SPI(0, baudrate=100000000, polarity=1, phase=1, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
#spi.init(baudrate=1000000, polarity=1, phase=1)
lcd = ST75256(256, 128, spi, Pin(1), Pin(0), display_cs, rot=0)
lcd.contrast(0x138)

lcd.fill(1)
lcd.show()
time.sleep(1)
lcd.fill(0)
lcd.show()
time.sleep(1)

wri = Writer(lcd, font7)
data = ["This is a test line[%02d], 12345678901234567" % i for i in range(18)] # 41 chars every line
#data = ["This is a test[%02d]" % i for i in range(36)] # 21 chars every line

x = 0
for n, line in enumerate(data):
    Writer.set_textpos(lcd, n * 7, x)
    wri.printstring(line)
lcd.show()
#lcd.fill(0)
#lcd.rect(10, 10, 128, 50, 1)
#lcd.show()
