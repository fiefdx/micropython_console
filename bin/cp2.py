import uos

from common import exists, path_join, isfile, isdir, path_split, mkdirs, copy


def main(*args, **kwargs):
    result = "invalid parameters"
    if len(args) == 2:
        s_path = args[0]
        t_path = args[1]
        cwd = uos.getcwd()
        if s_path.startswith("."):
            s_path = cwd + s_path[1:]
        if t_path.startswith("."):
            t_path = cwd + t_path[1:]
        copy(s_path, t_path)
        result = "copy finished"
    return result