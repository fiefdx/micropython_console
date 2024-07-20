import uos

from common import exists, path_join


def main(*args, **kwargs):
    result = "invalid parameters"
    if len(args) > 0:
        path = args[0]
        if not exists(path):
            with open(path, "w") as fp:
                pass
            result = path
    return result


