def find_key(key):
    # type: (str) -> str
    from os.path import expanduser, isdir, join, isfile, exists

    def dirs():
        yield "/dev/shm/.keys"
        yield expanduser("~/.keys")
        yield "/usr/share/.keys"

    if exists(key):
        return key
    for d in dirs():
        if isdir(d):
            k = join(d, key)
            if isfile(k):
                return k
            k = join(d, f"{key}.key")
            if isfile(k):
                return k
    raise FileNotFoundError(key)


def parse_keyfile(path):
    # type: (str) -> Dict[str, int]
    with open(path, "r") as r:
        return parse_key(r.read())


def parse_key(text):
    # type: (str) -> Dict[str, int]
    return literal_eval(text)


from ast import literal_eval
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict
