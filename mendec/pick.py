from .keyfile import parse_keyfile
from .utils import as_sink


def pick(keyfile="", which="", output="", **kwargs):
    desc = parse_keyfile(keyfile)

    if which in ("2", "d"):
        desc.pop("e")
    else:
        desc.pop("d")
    desc.pop("p", 0)
    desc.pop("q", 0)
    with as_sink(output, "w") as out:
        from pprint import pformat

        out.write(pformat(desc))
