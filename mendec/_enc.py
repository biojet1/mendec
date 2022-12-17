from sys import stdin, stdout, argv
from binascii import hexlify
from struct import pack
from io import RawIOBase, BufferedReader


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
    # type: (int) -> Generator[int, None, None]
    while 1:
        w = n & 0x7F
        n >>= 7
        if n:
            yield w | 0x80
        else:
            yield w
            break


def encode_stream(src, n):
    # type: (IO, int) -> None
    src.write(bytes(encode(n)))


def vencrypt(n, e, src, out):
    from random import SystemRandom

    # from sys import stderr

    random = SystemRandom()
    bits_max = n.bit_length()
    q, r = divmod(bits_max - 1, 8)
    bytes_max = q if q > 0 else q + 1
    getrandbits = random.getrandbits

    def mkprefix(x):
        return bytes(encode(getrandbits(random.randrange(32, 48)))) + bytes(encode(x))

    # print("bytes_max", bytes_max)
    i = 0
    prefix = mkprefix(i)
    # print("len(prefix)", len(prefix))
    block = src.read(bytes_max - len(prefix))
    while block:
        cypher = encrypt(prefix + block, n, e)
        # print('E', i, len(cypher), file=stderr)
        encode_stream(out, len(cypher))
        out.write(cypher)
        # print('blob', blob)
        i += 1
        prefix = mkprefix(i)
        block = src.read(bytes_max - len(prefix))


def main(N, E):
    r = stdin.buffer
    with r, stdout.buffer as w:
        vencrypt(N, E, r, w)


__name__ == "__main__" and main(744487561519699337969, 716435957194893448301)
{
    "": "70 bits, 8 bytes, 2022Dec17_073642",
    "d": 312084042341263374101,
    "e": 716435957194893448301,
    "n": 744487561519699337969,
}
