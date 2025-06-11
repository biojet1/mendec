"""Functions for parallel computation on multiple cores.

Copied from Python-RSA
"""

from multiprocessing import Process, Pipe

from .prime import is_prime
from .utils import read_random_odd_int

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


def _find_prime(nbits, pipe):
    # type: (int, Any) -> None
    while True:
        integer = read_random_odd_int(nbits)

        # Test for primeness
        if is_prime(integer):
            pipe.send(integer)
            return


def getprime(nbits, poolsize):
    # type: (int, int) -> int
    (pipe_recv, pipe_send) = Pipe(duplex=False)

    # Create processes
    try:
        procs = [
            Process(target=_find_prime, args=(nbits, pipe_send))
            for _ in range(poolsize)
        ]
        # Start processes
        for p in procs:
            p.start()

        result = pipe_recv.recv()
    finally:
        pipe_recv.close()
        pipe_send.close()

    # Terminate processes
    for p in procs:
        p.terminate()

    return result


__all__ = ["getprime"]
