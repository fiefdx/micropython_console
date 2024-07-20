from wifi import WIFI


def main(*args, **kwargs):
    WIFI.active(True)
    return "\n".join(WIFI.ifconfig())