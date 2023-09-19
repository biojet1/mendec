def main():
    from .parsearg import ArgumentParser

    cmd = ArgumentParser(prog="mendec")
    cmd.subparsers()
    from .cli.pick import pick
    from .cli.script import script
    from .cli.keygen import keygen, x8
    from .cli.encrypt import encrypt
    from .cli.decrypt import decrypt

    (
        cmd.sub("pick", help="extract key")
        .arg("keyfile", help="the key file to extract key")
        .arg(
            "which",
            choices=["1", "2", "e", "d"],
            help="which key to output",
        )
        .arg("output", default=None, help="save key to file")
        .call(pick)
    )
    (
        cmd.sub("script", help="create encryptor or decryptor script")
        .arg("keyfile", help="the key file to extract key")
        .arg(
            "which",
            choices=["encryptor", "decryptor"],
            help="encryptor or decryptor",
        )
        .arg("output", default=None, help="save key to file")
        .call(script)
    )
    (
        cmd.sub("keygen", help="create key")
        # --bits 256, -b 256
        .param("bits", "b", default=2048, type=int, help="How many bits")
        # --bytes 96, -B 96
        .param(
            "bytes",
            "B",
            type=x8,
            dest="bits",
            metavar="BYTES",
            help="How many bits in bytes",
        )
        # --pool 4, -p 4
        .param(
            "pool",
            "p",
            default=1,
            type=int,
            help="How many process to generate primes",
        )
        .param("output", "o", default=None, help="output to file")
        # --test, -t
        .bool("test", help="Test the generated key")
        # --near, -n
        .bool("near", dest="accurate", help="Not exact bits is ok")
        .call(keygen)
    )

    (
        cmd.sub("encrypt", help="encrypt using key")
        # 1st argument
        .arg("key", help="the key file")
        # 2nd argument
        .arg("message", default="", help="the message file")
        # --short, -s
        .flag("short", "s", help="short message encryption")
        # --output FILE, -o FILE
        .param("output", "o", default=None, help="output to file").call(encrypt)
    )
    (
        cmd.sub("decrypt", help="decrypt using key")
        # 1st argument
        .arg("key", help="the key file")
        # 2nd argument
        .arg("cypher", default="", help="the encrypted file")
        # --short, -s
        .flag("short", "s", help="short message encryption")
        # --output FILE, -o FILE
        .param("output", "o", default=None, help="output to file").call(decrypt)
    )

    cmd.parse_sub()


(__name__ == "__main__") and main()
