from ast import literal_eval


def parse_keyfile(path):
    with as_source(path, "rb") as r:
        d = r.read()
        h = d[0:15]
        if b"-----BEGIN PRIV" == h:
            pem = 1
        elif b"-----BEGIN PUBL" == h:
            pem = 2
        else:
            pem = 0
        if pem > 0:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa

            if pem == 1:
                pk = serialization.load_pem_private_key(d, None)
                return {
                    "e": pk.public_key().public_numbers().e,
                    "n": pk.public_key().public_numbers().n,
                    "d": pk.private_numbers().d,
                }
            else:
                pk = serialization.load_pem_public_key(d, None)
                return {
                    "e": pk.public_numbers().e,
                    "n": pk.public_numbers().n,
                }
        else:
            return parse_key(d.decode())


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
    desc.pop("p", 0)
    desc.pop("q", 0)
    with as_sink(app.output, "w") as out:
        from pprint import pformat

        out.write(pformat(desc))
