from nanocli import AppBase
from nanocli.extra import Expando


class Encrypt(AppBase, Expando):
    log_level = "INFO"
    dry_run = True
    app_name = "encrypt"
    key_enc = "e"
    key_dec = "d"

    def option(self, opt):
        if opt.pop_plain(doc="text to encrypt"):
            self.l_args.append(opt.value)
        elif opt.pop_bool("d", doc="Use the 'd' key to encrypt instead of 'e'"):
            if opt.value:
                self.key_enc = "d"
                self.key_dec = "e"
            else:
                self.key_enc = "e"
                self.key_dec = "d"
        else:
            super().option(opt)

    # @opt("d", "", doc="text to encrypt", take="")
    # def pop_plain(self, value=):
    #     self.l_args.append(opt.value)


    def start(self, *args, **kwargs):
        from sys import stdin, stdout
        from base64 import urlsafe_b64encode
        from .message import encrypt, decrypt

        out = stdout.buffer.write
        key = m = 0
        for x in self.l_args:
            if key:
                if m == 0:
                    out(b"\n")

                m = x.encode("UTF-8")
                c = encrypt(m, key[self.key_enc], key["e"])

                assert m == decrypt(
                    c, key[self.key_enc], key[self.key_dec]
                ), "message neq to cypher"
                out(urlsafe_b64encode(c))

            else:
                from ast import literal_eval

                path, sep, name = x.rpartition("#")
                if not path:
                    path, name = name, 0
                with open(path, "rb") as h:
                    desc = h.read()
                    a = desc.find(b"{")
                    b = desc.rfind(b"}")
                    desc = desc[a : b + 1]

                desc = literal_eval(desc.decode("UTF-8"))
                if name:
                    key = desc[name]
                else:
                    key = desc.popitem()[1]
                # key = (key.pop('n'), key.pop('e'), key.pop('d'))
                # print(key)
        if key and m == 0:
            m = stdin.read().strip().encode("UTF-8")
            c = encrypt(m, key[self.key_enc], key["e"])
            assert m == decrypt(
                c, key[self.key_enc], key[self.key_dec]
            ), "message neq to cypher"
            out(urlsafe_b64encode(c))


class KeyGen(AppBase):
    log_level = "INFO"
    app_name = "keygen"
    bits = 2048
    pool = 1
    accurate = True
    log_format = "%(asctime)s %(levelname)s: %(message)s"

    def option(self, opt):
        if opt.pop_string("bits", val="N", doc="How many bits"):
            self.bits = int(opt.value)
        elif opt.pop_string("bytes", val="N", doc="How many bits in bytes"):
            self.bits = int(opt.value) * 8
        elif opt.pop_string("pool", val="N", doc="How many process to generate primes"):
            self.pool = int(opt.value)
        elif opt.pop_bool("near", doc="Not exact bits is ok"):
            self.accurate = not opt.value
        else:
            super().option(opt)

    def start(self, *args, **kwargs):
        from time import time
        from datetime import datetime
        from sys import stdin, stdout, argv, platform, stderr
        from logging import info
        from .message import encrypt, decrypt
        from .key import newkeys

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

        t = platform.encode()

        print("{}\t{!r}".format(len(t), t), file=stderr)
        c = encrypt(t, n, e)
        print("{}\t{!r}".format(len(c), c), file=stderr)
        m = decrypt(c, n, d)
        print("{}\t{!r}".format(len(m), m), file=stderr)


def select(app_name):
    klass = 0
    for v in globals().values():
        n = getattr(v, "app_name", None)
        # print(v, getattr(v, "app_name", "?"))
        if not n or not n.startswith(app_name):
            pass
        elif klass:
            raise RuntimeError(
                "{!r} has two apps {!r} and {!r}".format(
                    app_name, v.app_name, klass.app_name
                )
            )
        else:
            klass = v
    # print(klass)
    if klass:
        return klass
    raise RuntimeError("No app {!r}".format(app_name))


if __name__ == "__main__":
    from sys import argv

    try:
        app_name = argv[1]
    except IndexError:
        raise RuntimeError("No app")
    else:
        select(app_name)().main(argv[2:])
