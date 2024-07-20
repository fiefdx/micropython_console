import uos

from common import exists, path_join


def main(*args, **kwargs):
    result = "path invalid"
    path = "/sd"
    if len(args) > 0:
        path = args[0]
    if exists(path) and uos.stat(path)[0] == 16384:
        uos.chdir(path)
        result = path
    return result

