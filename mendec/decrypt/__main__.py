#!/usr/bin/python3
from . import s_decrypt


def main(key="", cypher="", output="", **kwargs):
    from ..keyfile import find_key, parse_keyfile
    from ..utils import as_sink, as_source

    # parse the key file
    desc = parse_keyfile(find_key(key))
    # get n, e, d
    d = desc["d"] if "d" in desc else desc["e"]
    r = as_source(cypher)
    w = as_sink(output)
    with w, r:
        s_decrypt(r, w, desc["n"], d)


def supply(cli: "ArgumentParser"):
    cli.description = "Decrypt using key"
    cli.add_argument("key", help="the key file")
    cli.add_argument("cypher", help="the encrypted file", nargs="?")
    cli.add_argument("output", help="output to file", nargs="?")


if __name__ == "__main__":
    from argparse import ArgumentParser

    cli = ArgumentParser()
    supply(cli)
    main(**cli.parse_args().__dict__)
