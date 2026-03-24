from binascii import hexlify
from io import RawIOBase
from ..utils import int2bytes


def bytes2int(raw_bytes=b""):
    return int(hexlify(raw_bytes), 16)


def decrypt(crypto=b"", n=13, d=5):
    return int2bytes(pow(bytes2int(crypto), d, n))


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
