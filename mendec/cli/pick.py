from ocli import param, arg, flag, Main
from ocli.extra import BasicLog

from ast import literal_eval


def parse_keyfile(path):
    return parse_key(read_file(path))


def parse_key(text):
    return literal_eval(text)


def read_file(path):
    if path in ("-", None):
        from sys import stdin

        return stdin.read()
    with open(path, "r") as h:
        return h.read()


def write_to(path, blob):
    if path:
        with open(path, "wb") as h:
            out.write(blob)
    else:
        from sys import stdout

        stdout.buffer.write(blob)


def read_from(path):
    if path:
        with open(path, "rb") as h:
            return h.read()
    from sys import stdin

    return stdin.buffer.read()


def as_source(path):
    if path:
        return open(path, "rb")

    from sys import stdin

    return stdin.buffer


def as_sink(path):
    if path:
        return open(path, "wb")
    from sys import stdout

    return stdout.buffer


@arg("output", default="-", help="save key to file")
@arg("which", required=True, choices=["1", "2", "e", "d"], help="which key to output")
@arg("keyfile", required=True, help="the key file to extract key")
class Pick(BasicLog, Main):
    app_name = "pick"

    def start(self, *args, **kwargs):
        desc = parse_keyfile(self.keyfile)

        if self.which in ("2", "d"):
            desc.pop("e")
        else:
            desc.pop("d")

        if self.output == "-":
            from sys import stdout as out
        else:
            out = open(self.output, "w")
        from pprint import pformat

        with out:
            out.write(pformat(desc))

        from json import dumps
        import pprint


ENCS = ["b64", "ub64", "hex"]


@flag("short", "s", help="short message encryption", default=True)
@flag("encoding", "e", help="encoding to use", default=None, choices=ENCS)
@flag("output", "o", help="output to file", default=None)
class Crypt:
    pass


(__name__ == "__main__") and Pick().main()
