#!/usr/bin/python3

from binascii import hexlify
from struct import pack


def bytes2int(raw_bytes):
    # type: (bytes) -> int
    return int(hexlify(raw_bytes), 16)


def int2bytes(n):
    # type: (int) -> bytes
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


def encrypt(message, n, e):
    i = bytes2int(message)
    assert i <= n
    return int2bytes(pow(i, e, n))


def encode(n):
    while 1:
        w = n & 0x7F
        n >>= 7
        if n:
            yield w | 0x80
        else:
            yield w
            break


def encode_stream(src, n):
    src.write(bytes(encode(n)))


def vencrypt(n, e, src, out):
    from random import SystemRandom

    random = SystemRandom()
    bits_max = n.bit_length()
    q, r = divmod(bits_max - 1, 8)
    bytes_max = q if q > 0 else q + 1
    getrandbits = random.getrandbits

    def mkprefix(x):
        return bytes(encode(getrandbits(random.randrange(32, 48)))) + bytes(encode(x))

    i = 0
    prefix = mkprefix(i)
    block = src.read(bytes_max - len(prefix))
    while block:
        cypher = encrypt(prefix + block, n, e)
        encode_stream(out, len(cypher))
        out.write(cypher)
        i += 1
        prefix = mkprefix(i)
        block = src.read(bytes_max - len(prefix))


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
        vencrypt(N, X, r, w)  # noqa: F821 # undefined name
