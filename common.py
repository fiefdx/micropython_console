import os
import uos
import time
platform = "circuitpython"
supervisor = None
try:
    import supervisor
except:
    platform = "micropython"
    print("micropython, no supervisor module exists, use time.ticks_ms instead")

_TICKS_PERIOD = const(1<<29)
_TICKS_MAX = const(_TICKS_PERIOD-1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)


def ticks_ms():
    if supervisor:
        return supervisor.ticks_ms()
    else:
        return time.ticks_ms()


def sleep_ms(t):
    time.sleep(t / 1000.0)


def ticks_add(ticks, delta):
    # "Add a delta to a base number of ticks, performing wraparound at 2**29ms."
    return (ticks + delta) % _TICKS_PERIOD


def ticks_diff(ticks1, ticks2):
    # "Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
    diff = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff


def ticks_less(ticks1, ticks2):
    # "Return true iff ticks1 is less than ticks2, assuming that they are within 2**28 ticks"
    return ticks_diff(ticks1, ticks2) < 0


def exists(path):
    r = False
    try:
        if uos.stat(path):
            r = True
    except OSError:
        pass
    return r


def path_join(*args):
    path = args[0]
    for p in args[1:]:
        if path.endswith("/"):
            path = path[:-1]
        p = p.strip("/")
        if p.startswith(".."):
            path = "/".join(path.split("/")[:-1])
            path += "/" + p[2:]
        else:
            path += "/" + p
    if args[-1].endswith("/"):
        if not path.endswith("/"):
            path += "/"
    #if not path.startswith("/"):
    #    path = "/" + path
    return path


def isfile(path):
    return uos.stat(path)[0] == 32768


def isdir(path):
    return uos.stat(path)[0] == 16384


def path_split(path):
    parts = path.split("/")
    #if path.startswith("/"):
    #    parts[0] = "/"
    return "/".join(parts[:-1]), parts[-1]


def mkdirs(path):
    root, _ = path_split(path)
    if not exists(root):
        mkdirs(root)
    if not exists(path):
        uos.mkdir(path)


def copyfile(source, target):
    yield source
    with open(source, "rb") as s:
        with open(target, "wb") as t:
            buf_size = 2048
            buf = s.read(buf_size)
            while buf:
                t.write(buf)
                buf = s.read(buf_size)


def copydir(source, target):
    yield source
    if not exists(target):
        mkdirs(target)
        for f in uos.ilistdir(source):
            f = f[0]
            #print(path_join(source, f))
            s_path = path_join(source, f)
            t_path = path_join(target, f)
            if isfile(s_path):
                for output in copyfile(s_path, t_path):
                    yield output
            else:
                for output in copydir(s_path, t_path):
                    yield output


def copy(source, target):
    n = 1
    if exists(source):
        if not exists(target):
            if isfile(source):
                for output in copyfile(source, target):
                    yield "%s: %s" % (n, output)
                    n += 1
            else:
                for output in copydir(source, target):
                    yield "%s: %s" % (n, output)
                    n += 1
        else:
            yield "%s already exists!" % target
    else:
        yield "%s not exists!" % source
    
    
def rmtree(target):
    if exists(target):
        if isfile(target):
            uos.remove(target)
            yield target
            #uos.unlink(target)
        else:
            for f in uos.ilistdir(target):
                p = path_join(target, f[0])
                for output in rmtree(p):
                    yield output
            uos.rmdir(target)
            yield target
    
