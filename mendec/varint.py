from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generator, IO


def encode(n):
    # type: (int) -> Generator[int, None, None]
    """Encode an integer as a varint byte sequence."""
    # if n < 0:
    #     raise ValueError("Negative numbers not supported")
    while 1:
        w = n & 0x7F
        n >>= 7
        if n:
            yield w | 0x80
        else:
            yield w
            break


def encode_stream(src, n):
    # type: (IO[bytes], int) -> None
    """Write a varint to a binary stream."""
    src.write(bytes(encode(n)))


def decode_stream(src):
    # type: (IO[bytes]) -> int
    """Read a varint from a binary stream."""
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


def decode(blob):
    # type: (bytes) -> Generator[int, None, None]
    """Decode a byte string into a sequence of varints."""
    it = iter(blob)
    while 1:
        try:
            i = next(it)
        except StopIteration:
            break
        shift = result = 0
        while 1:
            result |= (i & 0x7F) << shift
            if not (i & 0x80):
                break
            i = next(it)
            shift += 7
        yield result
