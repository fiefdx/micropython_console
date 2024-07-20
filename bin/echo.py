import uos

from common import exists, path_join


def main(*args, **kwargs):
    result = "invalid parameters"
    if len(args) > 2:
        data = " ".join(args)
        if ">>" in data:
            content, path = data.split(">>")
            content = content.strip()
            if content.startswith("'") and content.endswith("'"):
                content = content[1:-1]
            elif content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            path = path.strip()
            with open(path, "a") as fp:
                fp.write(content)
            result = path
        elif ">" in data:
            content, path = data.split(">")
            content = content.strip()
            if content.startswith("'") and content.endswith("'"):
                content = content[1:-1]
            elif content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            path = path.strip()
            with open(path, "w") as fp:
                fp.write(content)
            result = path
    return result