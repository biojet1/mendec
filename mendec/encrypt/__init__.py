from binascii import hexlify
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
