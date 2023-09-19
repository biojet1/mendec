def script(app):
    from os.path import join, dirname
    from ..keyfile import parse_keyfile
    from .pick import as_source, as_sink

    desc = parse_keyfile(app.keyfile)
    cd = dirname(dirname(__file__))

    if app.which.startswith("e"):
        script = join(cd, "_enc.py")
        n, x = desc["n"], desc["e"]
    else:
        script = join(cd, "_dec.py")
        n, x = desc["n"], desc["d"]
    with as_source(script) as r, as_sink(app.output) as w:
        for c in r:
            if b"__name__" in c:
                w.write(f"N = {n}\n".encode())
                w.write(f"X = {x}\n".encode())
            if c.startswith(b"#") and c.strip() == b"#":
                break
            w.write(c)
