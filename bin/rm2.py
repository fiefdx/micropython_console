import uos

from common import exists, path_join, isfile, isdir, rmtree


def main(*args, **kwargs):
    result = "invalid parameters"
    if len(args) == 1:
        path = args[0]
        if isdir(path):
            uos.rmdir(path)
        else:
            uos.remove(path)
        result = path
    elif len(args) == 2 and args[0] == "-r":
        path = args[1]
        rmtree(path)
        result = path
    return result

