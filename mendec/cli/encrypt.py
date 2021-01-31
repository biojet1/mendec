from ocli import param, arg, flag, Main
from ocli.extra import Counter, BasicLog

from .pick import Crypt


@arg("message", default=None, help="the message file")
@arg("key", required=True, help="the key file")
class Encrypt(Crypt, BasicLog, Main):
    log_level = "INFO"
    app_name = "encrypt"

    def start(self, *args, **kwargs):
        from sys import stdout, stdin
        from ..message import encrypt, decrypt
        from .pick import parse_keyfile, write_to, read_from, as_source, as_sink

        # parse the key file
        desc = parse_keyfile(self.key)
        # get n, e, d
        e = desc["e"] if "e" in desc else desc["d"]
        if self.short:
            # get message
            message = read_from(self.message)
            # encrypt
            encrypted = encrypt(message, desc["n"], e)
            if self.encoding == "ub64":
                from base64 import urlsafe_b64encode as encode

            elif self.encoding == "b64":
                from base64 import b64encode as encode

            elif self.encoding == "hex":
                from binascii import hexlify as encode
            else:
                encode = None

            # output
            write_to(self.output, encode(encrypted) if encode else encrypted)
        else:
            from ..message import vencrypt
            with as_source(self.message) as r, as_sink(self.output) as w:
                vencrypt(desc["n"], e, r, w)


(__name__ == "__main__") and Encrypt().main()
