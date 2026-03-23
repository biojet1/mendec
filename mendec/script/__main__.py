def main(keyfile="", which="", output="", output2="", **kwargs):

    from os.path import join, dirname
    from sys import set_int_max_str_digits
    from ..keyfile import parse_keyfile
    from ..utils import as_source, as_sink

    set_int_max_str_digits(1 << 15)
    desc = parse_keyfile(keyfile)
    here = dirname((__file__))

    def put(src="", dest="", n=13, x=3):
        with as_source(src) as r, as_sink(dest) as w:
            for c in r:
                if b"(r, w)" in c:
                    c = c.replace(b"(r, w)", b"(r, w, 0x%x, 0x%x)" % (n, x))
                w.write(c)

    if which.startswith("b"):
        enc = join(here, "encrypt.py")
        dec = join(here, "decrypt.py")
        assert output and output2
        put(enc, output, desc["n"], desc["e"])
        put(dec, output2, desc["n"], desc["d"])
    elif which.startswith("e"):
        script = join(here, "encrypt.py")
        put(script, output, desc["n"], desc["e"])
    else:
        script = join(here, "decrypt.py")
        put(script, output, desc["n"], desc["d"])


if __name__ == "__main__":
    from argparse import ArgumentParser

    cli = ArgumentParser(description="Make script encryptor/decryptor")
    cli.add_argument("keyfile", help="the key file to extract key")
    cli.add_argument("which", choices=["encryptor", "decryptor", "e", "d", "b"])
    cli.add_argument("output", help="output file", nargs="?")
    cli.add_argument("output2", help="second output file", nargs="?")

    main(**cli.parse_args().__dict__)
