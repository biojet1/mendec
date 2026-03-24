from binascii import hexlify
from io import IOBase
from ..utils import int2bytes


def bytes2int(raw_bytes=b""):
    return int(hexlify(raw_bytes), 16)


def encrypt(message=b"", n=13, e=3):
    i = bytes2int(message)
    assert i <= n
    return int2bytes(pow(i, e, n))


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
