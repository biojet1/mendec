def main():
    from .decrypt.__main__ import main as decrypt, supply as supply_dec
    from .encrypt.__main__ import main as encrypt, supply as supply_enc
    from .script.__main__ import main as script, supply as supply_script
    from .keygen.keygen import x8, keygen
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
        # --test, -t
        .bool("test", help="Test the generated key")
        # --near, -n
        .bool("near", dest="accurate", help="Not exact bits is ok")
        .param("max-e-bits", dest="max_e_bits", help="Maximum bits of e")
        .arg("output", default=None, help="output to file")
    )
    if x := cmd.sub("script", call=lambda x: script(**x.__dict__)):
        supply_script(x)
    if x := cmd.sub("encrypt", call=lambda x: encrypt(**x.__dict__)):
        supply_enc(x)
    if x := cmd.sub("decrypt", call=lambda x: decrypt(**x.__dict__)):
        supply_dec(x)

    cmd.parse_args()


(__name__ == "__main__") and main()
