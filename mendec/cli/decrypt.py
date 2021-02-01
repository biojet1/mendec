from ocli import arg, Main
from ocli.extra import BasicLog

from .pick import Crypt


@arg("cypher", default=None, help="the encrypted file")
@arg("key", required=True, help="the key file")
class Decrypt(Crypt, BasicLog, Main):
    def start(self, *args, **kwargs):
        from .pick import parse_keyfile, as_source, as_sink

        # parse the key file
        desc = parse_keyfile(self.key)
        # get n, e, d
        d = desc["d"] if "d" in desc else desc["e"]
        if self.short:
            from ..message import decrypt

            with as_source(self.cypher) as r, as_sink(self.output) as w:
                w.write(decrypt(r.read(), desc["n"], d))
        else:
            from ..message import vdecrypt

            with as_source(self.cypher) as r, as_sink(self.output) as w:
                vdecrypt(desc["n"], d, r, w)


(__name__ == "__main__") and Decrypt().main()
