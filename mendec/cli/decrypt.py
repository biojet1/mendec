from ocli import Base
from ocli.extra import LogOpt
from .pick import Crypt


class Decrypt(Crypt, LogOpt, Base):
    def options(self, opt):
        opt.prog = "python -m mendec decrypt"
        super().options(
            opt
            # 1st argument
            .arg("key", required=True, help="the key file")
            # 2nd argument
            .arg("cypher", default=None, help="the encrypted file")
        )

    def start(self, *args, **kwargs):
        from .pick import as_source, as_sink
        from ..keyfile import find_key, parse_keyfile

        # parse the key file
        desc = parse_keyfile(find_key(self.key))
        # get n, e, d
        d = desc["d"] if "d" in desc else desc["e"]
        r = as_source(self.cypher)
        w = as_sink(self.output)
        if self.short:
            from ..message import decrypt

            with w, r:
                w.write(decrypt(r.read(), desc["n"], d))
        else:
            from ..message import vdecrypt

            with w, r:
                vdecrypt(desc["n"], d, r, w)


(__name__ == "__main__") and Decrypt().main()
