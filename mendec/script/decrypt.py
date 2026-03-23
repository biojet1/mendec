#!/usr/bin/python3
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


def decode_base64_source(src, n=None):
    from base64 import b64decode

    """Get a stream of decoded bytes from an iterable of base 64 bytes."""
    # https://stackoverflow.com/questions/55483846/python-stream-decode-base64-to-valid-utf8

    unprocessed = b""
    if not n:
        import io

        n = io.DEFAULT_BUFFER_SIZE
    chunk = src.read(n)

    while chunk:
        unprocessed += chunk.replace(b"\n", b"")

        safe_len = (len(unprocessed) // 4) * 4

        to_process, unprocessed = unprocessed[:safe_len], unprocessed[safe_len:]
        # print(len(to_process), len(unprocessed) , len(chunk) , safe_len)
        # missing_padding = len(data) % 4

        if to_process:
            yield b64decode(to_process)
        chunk = src.read(n)

    if unprocessed:
        yield b64decode(unprocessed + b"====")


if __name__ == "__main__":
    from sys import stdin, stdout, argv

    r, w = stdin.buffer, stdout.buffer
    if len(argv) > 1:
        if "-b" in argv:
            from io import RawIOBase, BufferedReader

            class IterStream(RawIOBase):
                def __init__(self, iterable):
                    self.leftover = b""
                    self.iterable = iterable

                def readable(self):
                    return True

                def readinto(self, b):
                    n = len(b)  # We're supposed to return at most this much
                    try:
                        chunk = self.leftover or next(self.iterable)
                    except StopIteration:
                        return 0  # indicate EOF
                    output, self.leftover = chunk[:n], chunk[n:]
                    b[: len(output)] = output
                    return len(output)

            r = BufferedReader(IterStream(decode_base64_source(r)))
        if "-x" in argv:
            from subprocess import Popen, PIPE
            from os import env

            p = Popen(env["SHELL"] or "/bin/sh", stdin=PIPE)
            w = p.stdin
    with r, w:
        s_decrypt(r, w)
