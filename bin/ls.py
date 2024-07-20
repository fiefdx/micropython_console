import uos

from common import exists, path_join


def main(*args, **kwargs):
    files = []
    dirs = []
    path = uos.getcwd()
    if len(args) > 0:
        path = args[0]
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    fs = uos.listdir(path)
    for f in fs:
        p = path_join(path, f)
        s = uos.stat(p)
        if s[0] == 16384:
            dirs.append("D:" + f)
        elif s[0] == 32768:
            files.append("F:" + f)
    result = "\n".join(dirs) + "\n" + "\n".join(files)
    return result
