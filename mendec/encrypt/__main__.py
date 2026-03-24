from . import s_encrypt


def main(key="", message="", output="", **kwargs):
    from ..keyfile import find_key, parse_keyfile
    from ..utils import as_sink, as_source

    # parse the key file
    desc = parse_keyfile(find_key(key))
    # get n, e, d
    e = desc["e"] if "e" in desc else desc["d"]
    r, w = as_source(message), as_sink(output)
    with w, r:
        s_encrypt(r, w, desc["n"], e)


def supply(cli: "ArgumentParser"):
    cli.description = "Encrypt using key"
    cli.add_argument("key", help="the key file")
    cli.add_argument("message", help="the message file", nargs="?")
    cli.add_argument("output", help="output file", nargs="?")


if __name__ == "__main__":
    from argparse import ArgumentParser

    cli = ArgumentParser()
    supply(cli)
    main(**cli.parse_args().__dict__)
