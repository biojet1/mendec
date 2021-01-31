from ocli import param, flag, Main
from ocli.extra import BasicLog


def x8(v):
    return int(v) * 8


@param("bits", "b", default=2048, type=int, help="How many bits")
@param("bytes", "B", type=x8, dest="bits", help="How many bits in bytes")
@param("pool", "p", default=1, type=int, help="How many process to generate primes")
@param("output", "o", help="output to file", default=None)
@flag("test", "t", default=True, help="Test the generated key")
@flag("near", "n", default=True, dest="accurate", help="Not exact bits is ok")
class KeyGen(BasicLog, Main):
    app_name = "keygen"
    log_format = "%(asctime)s %(levelname)s: %(message)s"

    def start(self, *args, **kwargs):
        from time import time
        from datetime import datetime
        from sys import platform
        from logging import info
        from ..message import encrypt, decrypt
        from ..key import newkeys
        from .pick import as_sink

        t = time()
        n, e, d = newkeys(self.bits, accurate=self.accurate, poolsize=self.pool)
        info("Duration %ss", time() - t)

        import pprint

        k = dict(n=n, e=e, d=d)
        max_bits = max(v.bit_length() for n, v in k.items())
        k[""] = "{} bits, {} bytes, {}".format(
            max_bits, max_bits // 8, (datetime.utcnow()).strftime("%Y%b%d_%H%M%S")
        )

        with as_sink(self.output, "w") as out:
            out.write("#")
            for x, v in k.items():
                if x:
                    out.write(
                        " {}:{}@{}".format(x, v.bit_length() // 8, v.bit_length())
                    )
            out.write("\n")

            pprint.pprint(k, stream=out)

        if self.test:
            data = dict(message=platform.encode())
            data["encrypted"] = encrypt(data["message"], n, e)
            data["decrypted"] = decrypt(data["encrypted"], n, d)

            if data["decrypted"] == data["message"]:
                info("test: passed")
            else:
                raise RuntimeError(
                    "Test failed message={message!r}, encrypted={encrypted!r}, decrypted={decrypted!r}".format(
                        **data
                    )
                )


(__name__ == "__main__") and KeyGen().main()
