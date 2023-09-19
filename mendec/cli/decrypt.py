def decrypt(app):
    from .pick import as_source, as_sink
    from ..keyfile import find_key, parse_keyfile

    # parse the key file
    desc = parse_keyfile(find_key(app.key))
    # get n, e, d
    d = desc["d"] if "d" in desc else desc["e"]
    r = as_source(app.cypher)
    w = as_sink(app.output)
    if app.short:
        from ..message import decrypt

        with w, r:
            w.write(decrypt(r.read(), desc["n"], d))
    else:
        from ..message import vdecrypt

        with w, r:
            vdecrypt(desc["n"], d, r, w)
