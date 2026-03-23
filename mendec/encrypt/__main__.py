from io import IOBase
from . import encrypt


def s_encrypt(src: IOBase, out: IOBase, n=13, e=3):
    m = n.bit_length()
    block_size, R = divmod(m, 8)
    block_size += 1 if R else 0
    bytes_max = divmod(m - 1, 8)[0]
    block = src.read(bytes_max)
    while block:
        assert len(block) <= bytes_max
        cur = block
        if len(cur) < bytes_max:
            block = b""
        else:
            block = src.read(bytes_max)
        if block:
            # there's next
            assert len(cur) == bytes_max
        else:
            assert len(cur) <= block_size
        cypher = encrypt(cur, n, e)
        c = len(cypher)
        if block:
            if c < block_size:
                cypher = (b"\0" * (block_size - c)) + cypher
                c = len(cypher)
            assert (
                c == block_size
            ), f"{dict(c=c,m=m,block_size=block_size,bytes_max=bytes_max,tell=src.tell())}"
        else:
            assert (
                c <= block_size and c >= bytes_max
            ), f"{dict(c=c,block_size=block_size,bytes_max=bytes_max,tell=src.tell())}"
        out.write(cypher)


# ------------


def main(key="", message="", output="", **kwargs):
    from ..keyfile import find_key, parse_keyfile
    from ..utils import as_sink, as_source

    # parse the key file
    desc = parse_keyfile(find_key(key))
    # get n, e, d
    e = desc["e"] if "e" in desc else desc["d"]
    r, w = as_source(message), as_sink(output)
    with w, r:
        s_encrypt(r, w, desc["n"], e)


if __name__ == "__main__":
    from argparse import ArgumentParser

    cli = ArgumentParser(description="encrypt using key")
    cli.add_argument("key", help="the key file")
    cli.add_argument("message", help="the message file")
    cli.add_argument("output", help="output file")

    main(**cli.parse_args().__dict__)
