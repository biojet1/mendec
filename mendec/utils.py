from binascii import hexlify
from struct import pack


def bytes2int(raw_bytes):
    return int(hexlify(raw_bytes), 16)


def byte_size(n):
    if n == 0:
        return 1
    q, r = divmod(n.bit_length(), 8)
    return (q + 1) if r else q


def int2bytes(number, block_size=0):
    if number < 0:
        raise ValueError("Negative numbers cannot be used: %i" % number)

    # Do some bounds checking
    if number == 0:
        needed_bytes = 1
        raw_bytes = [b"\x00"]
    else:
        needed_bytes = byte_size(number)
        raw_bytes = []

    if block_size > 0 and needed_bytes > block_size:
        raise OverflowError(
            "Needed %i bytes for number, but block size "
            "is %i" % (needed_bytes, block_size)
        )

    # Convert the number to bytes.
    while number > 0:
        raw_bytes.insert(0, pack("B", number & 0xFF))
        number >>= 8

    # Pad with zeroes to fill the block
    if block_size > 0:
        padding = (block_size - needed_bytes) * b"\x00"
    else:
        padding = b""

    return padding + b"".join(raw_bytes)

#########

from os import urandom

def read_random_bits(nbits):
    """Reads 'nbits' random bits.

    If nbits isn't a whole number of bytes, an extra byte will be appended with
    only the lower bits set.
    """

    nbytes, rbits = divmod(nbits, 8)

    # Get the random bytes
    randomdata = urandom(nbytes)

    # Add the remaining random bits
    if rbits > 0:
        randomvalue = ord(urandom(1))
        randomvalue >>= (8 - rbits)
        randomdata = pack("B", randomvalue) + randomdata

    return randomdata

def read_random_int(nbits):
    """Reads a random integer of approximately nbits bits.
    """

    randomdata = read_random_bits(nbits)
    value = bytes2int(randomdata)

    # Ensure that the number is large enough to just fill out the required
    # number of bits.
    value |= 1 << (nbits - 1)

    return value

def read_random_odd_int(nbits):
    """Reads a random odd integer of approximately nbits bits.

    >>> read_random_odd_int(512) & 1
    1
    """

    value = read_random_int(nbits)

    # Make sure it's odd
    return value | 1


def randint(maxvalue):
    """Returns a random integer x with 1 <= x <= maxvalue

    May take a very long time in specific situations. If maxvalue needs N bits
    to store, the closer maxvalue is to (2 ** N) - 1, the faster this function
    is.
    """

    bit_size = maxvalue.bit_length()

    tries = 0
    while True:
        value = read_random_int(bit_size)
        if value <= maxvalue:
            break

        if tries % 10 == 0 and tries:
            # After a lot of tries to get the right number of bits but still
            # smaller than maxvalue, decrease the number of bits by 1. That'll
            # dramatically increase the chances to get a large enough number.
            bit_size -= 1
        tries += 1

    return value

