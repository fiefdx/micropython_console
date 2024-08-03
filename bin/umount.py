import uos

from common import exists, path_join


def main(*args, **kwargs):
    result = "invalid parameters"
    sd = kwargs["sd"]
    vfs = kwargs["vfs"]
    if len(args) > 0:
        path = args[0]
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        uos.umount(path)
        sd = None
        vfs = None
        result = "success"
    return result, sd, vfs