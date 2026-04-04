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


def encrypt(message=b"", n=13, e=3):
    i = bytes2int(message)
    assert i <= n
    return int2bytes(pow(i, e, n))


def s_encrypt(src: RawIOBase, out: RawIOBase, n=13, e=3):
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

    # Get a stream of decoded bytes from an iterable of base 64 bytes
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
    from argparse import ArgumentParser
    from sys import stdin, stdout

    a = ArgumentParser()
    a.add_argument("-b", action="store_true", help="in/out is base64 encoded")
    a.add_argument("what", choices=["encrypt", "decrypt", "e", "d"])
    o = a.parse_args()
    d = o.what.startswith("d")
    b = o.b
    n = 13
    x = 7
    r, w = stdin.buffer, stdout.buffer
    if d:
        if b:
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
        with r, w:
            s_decrypt(r, w, n, x)
    else:
        if b:
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
            s_encrypt(r, w, n, x)
