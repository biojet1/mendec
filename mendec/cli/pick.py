from ast import literal_eval


def parse_keyfile(path):
    with as_source(path, "r") as r:
        return parse_key(r.read())


def parse_key(text):
    return literal_eval(text)


def as_source(path, mode="rb"):
    if path and path != "-":
        return open(path, mode)
    from sys import stdin

    return stdin.buffer if "b" in mode else stdin


def as_sink(path, mode="wb"):
    if path and path != "-":
        return open(path, mode)
    from sys import stdout

    return stdout.buffer if "b" in mode else stdout


def pick(app):
    desc = parse_keyfile(app.keyfile)

    if app.which in ("2", "d"):
        desc.pop("e")
    else:
        desc.pop("d")

    with as_sink(app.output, "w") as out:
        from pprint import pformat

        out.write(pformat(desc))
