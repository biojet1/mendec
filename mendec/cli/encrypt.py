def encrypt(app):
    from .pick import as_source, as_sink
    from ..keyfile import find_key, parse_keyfile

    # parse the key file
    desc = parse_keyfile(find_key(app.key))
    # get n, e, d
    e = desc["e"] if "e" in desc else desc["d"]
    r, w = as_source(app.message), as_sink(app.output)

    if app.short:
        from ..message import encrypt

        with w, r:
            w.write(encrypt(r.read(), desc["n"], e))
    else:
        from ..message import vencrypt

        with w, r:
            vencrypt(desc["n"], e, r, w)
