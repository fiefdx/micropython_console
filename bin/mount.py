import uos

import sdcard
from common import exists, path_join


def main(*args, **kwargs):
    result = "invalid parameters"
    sd = kwargs["sd"]
    vfs = kwargs["vfs"]
    spi = kwargs["spi"]
    sd_cs = kwargs["sd_cs"]
    if len(args) > 0:
        path = args[0]
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        sd = sdcard.SDCard(spi, sd_cs, baudrate=13200000)
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, "/sd")
        result = "success"
    return result, sd, vfs
