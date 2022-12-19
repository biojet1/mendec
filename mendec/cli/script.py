from ocli import Base
from ocli.extra import LogOpt


class Script(LogOpt, Base):
    app_name = "script"

    def options(self, opt):
        opt.prog = "python -m mendec script"
        super().options(
            opt
            # first argument
            .arg("keyfile", required=True, help="the key file to extract key")
            # second argument
            .arg(
                "which",
                required=True,
                choices=["encryptor", "decryptor"],
                help="which script to output",
            )
            # third argument
            .arg("output", default=None, help="save key to file")
        )

    def start(self, *args, **kwargs):
        from os.path import join, dirname
        from ..keyfile import parse_keyfile
        from .pick import as_source, as_sink

        desc = parse_keyfile(self.keyfile)
        cd = dirname(dirname(__file__))

        if self.which.startswith("e"):
            script = join(cd, "_enc.py")
            n, x = desc["n"], desc["e"]
        else:
            script = join(cd, "_dec.py")
            n, x = desc["n"], desc["d"]
        with as_source(script) as r, as_sink(self.output) as w:
            for c in r:
                if b"__name__" in c:
                    w.write(f"N = {n}\n".encode())
                    w.write(f"X = {x}\n".encode())
                if c.startswith(b'#') and c.strip() == b'#':
                    break
                w.write(c)


(__name__ == "__main__") and Script().main()
