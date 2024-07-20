import network
import socket


class WIFI(object):
    wlan = network.WLAN(network.STA_IF)
    ssid = ""
    password = ""
        
    @classmethod
    def active(cls, flag):
        cls.wlan.active(flag)
        
    @classmethod
    def is_connect(cls):
        return cls.wlan.isconnected()
    
    @classmethod
    def connect(cls, ssid, password):
        cls.ssid = ssid
        cls.password = password
        cls.wlan.connect(ssid, password)
        
    @classmethod
    def disconnect(cls):
        cls.wlan.disconnect()
        
    @classmethod
    def reconnect(cls):
        cls.wlan.connect(cls.ssid, cls.password)
        
    @classmethod
    def scan(cls):
        return cls.wlan.scan()
        
    @classmethod
    def ifconfig(cls):
        return cls.wlan.ifconfig()
        