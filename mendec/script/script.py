from ..utils import as_sink


def script(keyfile="", which="e", output="-"):
    from os.path import join, dirname
    from ..keyfile import parse_keyfile
    from ..utils import as_source

    desc = parse_keyfile(keyfile)
    cd = dirname(dirname(__file__))

    if which.startswith("e"):
        script = join(cd, "_enc.py")
        n, x = desc["n"], desc["e"]
    else:
        script = join(cd, "_dec.py")
        n, x = desc["n"], desc["d"]
    with as_source(script) as r, as_sink(output) as w:
        for c in r:
            if b"__name__" in c:
                w.write(f"N = {n}\n".encode())
                w.write(f"X = {x}\n".encode())
            if c.startswith(b"#") and c.strip() == b"#":
                break
            w.write(c)
