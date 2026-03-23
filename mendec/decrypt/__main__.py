#!/usr/bin/python3


from io import RawIOBase

from . import decrypt

from ..utils import as_sink, as_source


def s_decrypt(src: RawIOBase, out: RawIOBase, n=13, d=5):
    m = n.bit_length()
    block_size, R = divmod(m, 8)
    block_size += 1 if R else 0
    cypher = src.read(block_size)
    while cypher:
        next_cypher = src.read(block_size)
        if next_cypher:
            assert len(cypher) == block_size
        blob = decrypt(cypher, n, d)
        out.write(blob)
        cypher = next_cypher


# ------------
def main(key="", cypher="", output="", **kwargs):
    from ..keyfile import find_key, parse_keyfile

    # parse the key file
    desc = parse_keyfile(find_key(key))
    # get n, e, d
    d = desc["d"] if "d" in desc else desc["e"]
    r = as_source(cypher)
    w = as_sink(output)
    with w, r:
        s_decrypt(r, w, desc["n"], d)


if __name__ == "__main__":
    from argparse import ArgumentParser

    cli = ArgumentParser(description="encrypt using key")
    cli.add_argument("key", help="the key file")
    cli.add_argument("cypher", help="the encrypted file")
    cli.add_argument("output", help="output to file")

    main(**cli.parse_args().__dict__)
