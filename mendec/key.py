from logging import debug, info, error
from math import gcd
from secrets import randbelow
from .utils import randint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Tuple


def extended_gcd(a, b):
    # type: (int, int) -> Tuple[int, int, int]
    """Returns a tuple (r, i, j) such that r = gcd(a, b) = ia + jb"""
    # r = gcd(a,b) i = multiplicitive inverse of a mod b
    #      or      j = multiplicitive inverse of b mod a
    # Neg return values for i or j are made positive mod b or a respectively
    # Iterateive Version is faster and uses much less stack space
    x = 0
    y = 1
    lx = 1
    ly = 0
    oa = a  # Remember original a/b to remove
    ob = b  # negative values from return results
    while b != 0:
        q = a // b
        (a, b) = (b, a % b)
        (x, lx) = ((lx - (q * x)), x)
        (y, ly) = ((ly - (q * y)), y)
    if lx < 0:
        lx += ob  # If neg wrap modulo orignal b
    if ly < 0:
        ly += oa  # If neg wrap modulo orignal a
    return a, lx, ly  # Return only positive values


class NotRelativePrimeError(ValueError):
    def __init__(self, a, b, d, msg=""):
        # type: (int, int, int, str) -> None
        super(NotRelativePrimeError, self).__init__(
            msg or "%d and %d are not relatively prime, divider=%i" % (a, b, d)
        )
        self.a = a
        self.b = b
        self.d = d


def inverse(x, n):
    # type: (int, int) -> int
    """Returns the inverse of x % n under multiplication, a.k.a x^-1 (mod n)

    >>> inverse(7, 4)
    3
    >>> (inverse(143, 4) * 143) % 4
    1
    """

    (divider, inv, _) = extended_gcd(x, n)

    if divider != 1:
        raise NotRelativePrimeError(x, n, divider)

    return inv


def find_p_q(nbits, getprime_func, accurate=True):
    # type: (int, Callable[[int], int], bool) -> Tuple[int, int]
    total_bits = nbits * 2

    # Make sure that p and q aren't too close or the factoring programs can
    # factor n.
    shift = nbits // 16
    pbits = nbits + shift
    qbits = nbits - shift

    # Choose the two initial primes
    debug("find_p_q(%i): Finding p", nbits)
    p = getprime_func(pbits)
    debug("find_p_q(%i): Finding q", nbits)
    q = getprime_func(qbits)

    def is_acceptable(p, q):
        """Returns True iff p and q are acceptable:

        - p and q differ
        - (p * q) has the right nr of bits (when accurate=True)
        """

        if p == q:
            return False

        if not accurate:
            return True

        # Make sure we have just the right amount of bits
        found_size = (p * q).bit_length()
        return total_bits == found_size

    # Keep choosing other primes until they match our requirements.
    change_p = False
    while not is_acceptable(p, q):
        # Change p on one iteration and q on the other
        if change_p:
            debug("p and q not acceptable, finding p")
            p = getprime_func(pbits)
        else:
            debug("p and q not acceptable, finding q")
            q = getprime_func(qbits)

        change_p = not change_p

    # We want p > q as described on
    # http://www.di-mgt.com.au/rsa_alg.html#crt
    return max(p, q), min(p, q)


# def calculate_keys_custom_exponent(p, q):
#     # type: (int, int) -> Tuple[int, int]
#     """Calculates an encryption and a decryption key given p, q and an exponent,
#     and returns them as a tuple (e, d)

#     :param p: the first large prime
#     :param q: the second large prime
#     :param exponent: the exponent for the key; only change this if you know
#         what you're doing, as the exponent influences how difficult your
#         private key can be cracked. A very common choice for e is 65537.
#     :type exponent: int

#     """

#     phi_n = (p - 1) * (q - 1)

#     while 1:
#         try:
#             exponent = randint(phi_n)

#             d = inverse(exponent, phi_n)
#             break
#         except NotRelativePrimeError as ex:
#             error("{!r} try again".format(ex))

#     if (exponent * d) % phi_n != 1:
#         raise ValueError(
#             "e (%d) and d (%d) are not mult. inv. modulo "
#             "phi_n (%d)" % (exponent, d, phi_n)
#         )

#     return exponent, d


def calculate_keys_custom_exponent(
    p: int,
    q: int,
    e: int = 0,
    min_e: int = 3,  # Changed from 65537 to allow smaller e
    max_e_bits: int = 32,  # Upper bound for random e generation
    max_attempts=1000,
):
    """Generates RSA keys while allowing smaller secure e values.

    Args:
        p, q: Large distinct primes
        e: If non-zero, use this exponent (must be valid)
        min_e: Minimum exponent value (default 3)
        max_e_bits: Maximum bits for random e (default 32, ~4 billion)

    Returns:
        Tuple of (e, d)

    Raises:
        ValueError: For invalid parameters or unsafe keys
    """
    # Input validation
    if p == q:
        raise ValueError("p and q must be distinct primes")
    if p < 2 or q < 2:
        raise ValueError("p and q must be > 1")
    phi_n = (p - 1) * (q - 1)

    # Handle custom e
    if e != 0:
        if e < min_e:
            raise ValueError(f"e must be ≥ {min_e}")
        if e >= phi_n:
            raise ValueError("e must be < ϕ(n)")
        if gcd(e, phi_n) != 1:
            raise ValueError("e must be coprime with ϕ(n)")
        d = pow(e, -1, phi_n)
        _validate_private_exponent(d, phi_n.bit_length())
        return e, d

    # Generate random e with new constraints
    if min_e < 3:
        if min_e == 0 and max_e_bits > 4:
            min_e = 2**max_e_bits - 3
        else:
            raise ValueError("min_e must be ≥ 3 for security")

    max_possible_e = min(phi_n - 1, 2**max_e_bits - 1)
    if min_e > max_possible_e:
        raise ValueError(f"No valid e exists between {min_e} and {max_possible_e}")

    for _ in range(max_attempts):  # Try 1000 random candidates
        e = randbelow(max_possible_e - min_e + 1) + min_e
        if gcd(e, phi_n) == 1:
            d = pow(e, -1, phi_n)
            _validate_private_exponent(d, phi_n.bit_length())
            return e, d

    raise ValueError("Failed to find suitable e after 1000 attempts")


def _validate_private_exponent(d: int, phi_n_bits: int) -> None:
    """Ensure d meets security requirements."""
    min_d_bits = min(256, phi_n_bits // 2)  # At least 256 bits or half of ϕ(n) bits
    if d.bit_length() < min_d_bits:
        raise ValueError(
            f"Private exponent d is too small ({d.bit_length()} bits). "
            f"Must be ≥ {min_d_bits} bits for security."
        )


def gen_keys(
    nbits,
    getprime_func,
    accurate=True,
    e=0,
    min_e=3,  # Changed from 65537 to allow smaller e
    max_e_bits=32,  # Upper bound for random e generation
    max_attempts=1000,
):
    i = 0
    while True:
        i += 1
        info("%r\tFind p, q", i)
        (p, q) = find_p_q(nbits // 2, getprime_func, accurate)
        try:
            info("\tCalc e, d")
            # print("calc", [e, min_e, max_e_bits, max_attempts])
            (e, d) = calculate_keys_custom_exponent(
                p, q, e, min_e, max_e_bits, max_attempts
            )
            break
        except ValueError:
            pass

    return p, q, e, d


def newkeys(
    nbits,
    accurate=True,
    poolsize=1,
    use_e=0,
    min_e=3,  # Changed from 65537 to allow smaller e
    max_e_bits=32,  # Upper bound for random e generation
    max_attempts=1000,
):

    if nbits < 16:
        raise ValueError("Key too small")

    if poolsize < 1:
        raise ValueError("Pool size (%i) should be >= 1" % poolsize)

    # Determine which getprime function to use
    if poolsize > 1:
        from .parallel import getprime as getprimep
        from functools import partial

        # Generate the key components
        (p, q, e, d) = gen_keys(
            nbits,
            partial(getprimep, poolsize=poolsize),
            accurate,
            use_e,
            min_e,
            max_e_bits,
            max_attempts,
        )
    else:
        from .prime import getprime

        # Generate the key components
        (p, q, e, d) = gen_keys(
            nbits, getprime, accurate, use_e, min_e, max_e_bits, max_attempts
        )

    # Create the key objects
    n = p * q

    return n, e, d, p, q
