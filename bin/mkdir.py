import uos

from common import exists, path_join, mkdirs


def main(*args, **kwargs):
    result = "already exists!"
    cwd = uos.getcwd()
    if len(args) > 0:
        path = args[0]
        if path.startswith("."):
            path = cwd + path[1:]
        if path.endswith("/"):
            path = path[:-1]
        if not exists(path):
            mkdirs(path)
            result = path
    return result
