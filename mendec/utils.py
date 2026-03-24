"""
Copied from Python-RSA
"""

from struct import pack


def byte_size(n):
    # type: (int) -> int
    if n == 0:
        return 1
    q, r = divmod(n.bit_length(), 8)
    return (q + 1) if r else q


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


def as_sink(path, mode="wb"):
    if path and path != "-":
        return open(path, mode)
    from sys import stdout

    return stdout.buffer if "b" in mode else stdout


def as_source(path, mode="rb"):
    if path and path != "-":
        return open(path, mode)
    from sys import stdin

    return stdin.buffer if "b" in mode else stdin


#########
