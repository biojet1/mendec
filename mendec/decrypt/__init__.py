from binascii import hexlify
from io import RawIOBase
from struct import pack


def bytes2int(raw_bytes=b""):
    return int(hexlify(raw_bytes), 16)


def int2bytes(n=13):
    if n < 0:
        raise ValueError("Negative numbers cannot be used: %i" % n)
    elif n == 0:
        return b"\x00"
    a = []
    while n > 0:
        a.append(pack("B", n & 0xFF))
        n >>= 8
    a.reverse()
    return b"".join(a)


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
