def main():
    from .keygen.keygen import x8, keygen
    from .decrypt.__main__ import main as decrypt
    from .encrypt.__main__ import main as encrypt
    from .script.__main__ import main as script
    from .pick import pick
    from .parsearg import ArgumentParserEx

    cmd = ArgumentParserEx(prog="mendec")

    (
        cmd.sub("pick", call=lambda x: pick(**x.__dict__), help="extract key")
        .arg("keyfile", help="the key file to extract key")
        .arg(
            "which",
            choices=["1", "2", "e", "d"],
            help="which key to output",
        )
        .arg("output", default=None, help="save key to file")
    )
    (
        cmd.sub(
            "script",
            call=lambda x: script(**x.__dict__),
            help="create encryptor or decryptor script",
        )
        .arg("keyfile", help="the key file to extract key")
        .arg(
            "which",
            choices=["encryptor", "decryptor", "both", "b", "e", "d"],
            help="encryptor or decryptor",
        )
        .arg("output", default=None, help="save key to file")
        .arg("output2", default=None, help="save second key to file")
    )
    (
        cmd.sub("keygen", call=lambda x: keygen(**x.__dict__), help="create key")
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
        .param("max-e-bits", dest="max_e_bits", help="Maximum bits of e")
    )

    (
        cmd.sub(
            "encrypt", call=lambda x: encrypt(**x.__dict__), help="encrypt using key"
        )
        .arg("key", help="the key file")
        .arg("message", default="", help="the message file")
        .arg("output", "o", default=None, help="output to file")
    )
    (
        cmd.sub(
            "decrypt", call=lambda x: decrypt(**x.__dict__), help="decrypt using key"
        )
        .arg("key", help="the key file")
        .arg("cypher", default="", help="the encrypted file")
        .arg("output", "o", default=None, help="output to file")
    )

    cmd.parse_args()


(__name__ == "__main__") and main()
