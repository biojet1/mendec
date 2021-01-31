from ocli import param, arg, flag, Main
from ocli.extra import Counter, BasicLog

from .pick import Crypt


@arg("cypher", default=None, help="the encrypted file")
@arg("key", required=True, help="the key file")
class Decrypt(Crypt, BasicLog, Main):
    app_name = "decrypt"

    def start(self, *args, **kwargs):
        from ..message import encrypt, decrypt
        from .pick import parse_keyfile, write_to, read_from, as_source, as_sink

        # parse the key file
        desc = parse_keyfile(self.key)
        # get n, e, d
        d = desc["d"] if "d" in desc else desc["e"]
        if self.short:
            # decrypt
            cypher = read_from(self.cypher)

            if self.encoding == "ub64":
                from base64 import urlsafe_b64decode as decode
            elif self.encoding == "b64":
                from base64 import b64decode as decode
            elif self.encoding == "hex":
                from binascii import unhexlify as decode
            else:
                decode = None

            decrypted = decrypt(decode(cypher) if decode else cypher, desc["n"], d)
            # output
            write_to(self.output, decrypted)
        else:
            from ..message import vdecrypt

            with as_source(self.cypher) as r, as_sink(self.output) as w:
                vdecrypt(desc["n"], d, r, w)


(__name__ == "__main__") and Decrypt().main()
