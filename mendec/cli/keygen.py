from ocli import param, arg, flag, Main
from ocli.extra import BasicLog

x8 = lambda v: int(v) * 8


@param("bits", "b", default=2048, type=int, help="How many bits")
@param("bytes", "B", type=x8, dest="bits", help="How many bits in bytes")
@param("pool", "p", default=1, type=int, help="How many process to generate primes")
@flag("test", "t", default=True, help="Test the generated key")
@flag("near", "n", default=True, dest="accurate", help="Not exact bits is ok")
class KeyGen(BasicLog, Main):
    app_name = "keygen"
    log_format = "%(asctime)s %(levelname)s: %(message)s"

    def start(self, *args, **kwargs):
        from time import time
        from datetime import datetime
        from sys import stdin, stdout, argv, platform, stderr, exit
        from logging import info, error
        from ..message import encrypt, decrypt
        from ..key import newkeys

        t = time()
        n, e, d = newkeys(self.bits, accurate=self.accurate, poolsize=self.pool)
        info("Duration %ss", time() - t)

        from json import dumps
        import pprint

        k = dict(n=n, e=e, d=d)
        max_bits = max(v.bit_length() for n, v in k.items())
        k[""] = "{} bits, {} bytes, {}".format(
            max_bits, max_bits // 8, (datetime.utcnow()).strftime("%Y%b%d_%H%M%S")
        )

        print(
            "#"
            + " ".join(
                "{}:{}@{}".format(n, v.bit_length() // 8, v.bit_length())
                for n, v in k.items()
                if n
            )
        )
        pprint.pprint(k)

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
