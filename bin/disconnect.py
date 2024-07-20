import time
from wifi import WIFI


def main(*args, **kwargs):
    WIFI.disconnect()
    WIFI.active(False)
    return "\n".join(WIFI.ifconfig())
