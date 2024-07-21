import os
import gc
import time
import uos
from machine import Pin, SPI

from UC1609 import UC1609
import font7
from writer import Writer

display_cs = machine.Pin(5, machine.Pin.OUT)
spi = SPI(0, baudrate=1000000, polarity=1, phase=1, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
spi.init(baudrate=15000000, polarity=1, phase=1)
lcd = UC1609(spi, Pin(1), display_cs, Pin(0))

wri = Writer(lcd, font7)
data = ["This is a test line[%d], 12345678" % i for i in range(9)] # 32 chars every line
x = 0
for n, line in enumerate(data):
    Writer.set_textpos(lcd, n * 7, x)
    wri.printstring(line)
lcd.show()

