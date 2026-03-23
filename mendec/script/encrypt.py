#!/usr/bin/python3
from binascii import hexlify
from io import IOBase
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
        cypher = encrypt(cur, n, e)
        c = len(cypher)
        if block:
            if c < block_size:
                cypher = (b"\0" * (block_size - c)) + cypher
        out.write(cypher)


if __name__ == "__main__":
    from sys import stdin, stdout, argv

    r, w = stdin.buffer, stdout.buffer
    if len(argv) > 1:
        if "-b" in argv:
            from io import RawIOBase
            from base64 import b64encode

            class Base64Sink(RawIOBase):
                def __init__(self, sink):
                    self.surplus = b""
                    self.sink = sink

                def close(self):
                    sink = self.sink
                    data = self.surplus
                    data and sink.write(b64encode(data))
                    sink.close()
                    self.surplus = b""

                def write(self, blob):
                    data = self.surplus + blob
                    safe_len = (len(data) // 3) * 3
                    push, self.surplus = data[:safe_len], data[safe_len:]
                    push and self.sink.write(b64encode(push))

                def readable(self):
                    return False

                def writable(self):
                    return True

                def seekable(self):
                    return False

            w = Base64Sink(w)
    with w, r:
        s_encrypt(r, w)
