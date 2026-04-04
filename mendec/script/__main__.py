from ..utils import as_sink


def supply(cli: "ArgumentParser"):
    cli.description = "Make script pair encryptor <--/--> decryptor"
    cli.add_argument("keyfile", help="the key file to extract key")
    cli.add_argument("script1", help="first script")
    cli.add_argument("script2", help="second script")


def main(keyfile="key", script1="alice", script2="bob", **kwargs):
    from os.path import join, dirname
    from ..keyfile import parse_keyfile
    from ..utils import as_source

    desc = parse_keyfile(keyfile)
    script = join(dirname(__file__), "_script.py")
    n = desc["n"]
    for scriptx, x in ((script1, desc["e"]), (script2, desc["d"])):
        with as_source(script) as r, as_sink(scriptx) as w:
            for c in r:
                for f, g in ((b"    n = ", n), (b"    x = ", x)):
                    if c.startswith(f):
                        h, s, _ = c.rpartition(b" = ")
                        w.write(h + s)
                        w.write(f"0x{g:x}\n".encode())
                        break
                else:
                    if c.strip().startswith(b"# "):
                        continue
                    w.write(c)


if __name__ == "__main__":
    from argparse import ArgumentParser

    cli = ArgumentParser()
    supply(cli)
    main(**cli.parse_args().__dict__)
