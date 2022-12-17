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


def decrypt(crypto, n, d):
    return int2bytes(pow(bytes2int(crypto), d, n))


def decode_stream(src):
    # type: (IO) -> int
    b = src.read(1)
    if b:
        shift = result = 0
        while 1:
            i = ord(b)
            result |= (i & 0x7F) << shift
            if not (i & 0x80):
                break
            shift += 7
            b = src.read(1)
        return result
    else:
        return -1


def vdecrypt(n, d, src, out, i=0):
    from io import BytesIO

    s = decode_stream(src)
    while s > 0:
        cypher = src.read(s)
        blob = decrypt(cypher, n, d)
        # print('D', i, s, len(blob))
        b = BytesIO(blob)
        salt = decode_stream(b)
        index = decode_stream(b)
        block = b.read()
        assert index == i
        assert salt != 0
        out.write(block)
        i += 1
        s = decode_stream(src)


def decode_base64_source(src, n=None):
    from base64 import b64decode, standard_b64decode

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


class IterStream(RawIOBase):
    def __init__(self, iterable):
        self.leftover = None
        self.iterable = iterable

    def readable(self):
        return True

    def readinto(self, b):
        l = len(b)  # We're supposed to return at most this much
        try:
            chunk = self.leftover or next(self.iterable)
        except StopIteration:
            return 0  # indicate EOF
        output, self.leftover = chunk[:l], chunk[l:]
        b[: len(output)] = output
        return len(output)


#     return io.BufferedReader(IterStream(), buffer_size=buffer_size)


# def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
#     """
#     Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only
#     input stream.

#     The stream implements Python 3's newer I/O API (available in Python 2's io module).
#     For efficiency, the stream is buffered.
#     """
#     class IterStream(io.RawIOBase):
#         def __init__(self):
#             self.leftover = None
#         def readable(self):
#             return True
#         def readinto(self, b):
#             try:
#                 l = len(b)  # We're supposed to return at most this much
#                 chunk = self.leftover or next(iterable)
#                 output, self.leftover = chunk[:l], chunk[l:]
#                 b[:len(output)] = output
#                 return len(output)
#             except StopIteration:
#                 return 0    # indicate EOF
#     return io.BufferedReader(IterStream(), buffer_size=buffer_size)

if len(argv) > 1 and ("-b" in argv):
    r = BufferedReader(IterStream(decode_base64_source(stdin.buffer)))
else:
    r = stdin.buffer
with r, stdout.buffer as w:
    vdecrypt(N, D, r, w)

# data = rb"""TGludXggQUtJVEEgNS4xNS4wLTU2LWdlbmVyaWMgIzYyLVVidW50dSBTTVAgVHVlIE5vdiAyMiAx
# OTo1NDoxNCBVVEMgMjAyMiB4ODZfNjQgeDg2XzY0IHg4Nl82NCBHTlUvTGludXgK"""
# # Linux AKITA 5.15.0-56-generic #62-Ubuntu SMP Tue Nov 22 19:54:14 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
# from io import BytesIO

# # i = decode_base64_source(BytesIO(data), 63)

# # print(next(i))
# # print(next(i))
# # print(next(i))

# # r = BufferedReader(IterStream(decode_base64_source(BytesIO(data), 96)))
# r = BufferedReader(IterStream(decode_base64_source(stdin.buffer, 96)))
# print(r.read(63))
# print(r.read(63))
# print(r.read(63))


# # print(next(i))
