def x8(v):
    return int(v) * 8


def keygen(
    max_e_bits=32, bits=2048, accurate=True, pool=1, output="-", test=False, **kwargs
):
    from datetime import datetime
    from logging import info
    from sys import platform, set_int_max_str_digits
    from time import time

    from . import newkeys
    from ..encrypt import encrypt
    from ..decrypt import decrypt
    from ..utils import as_sink

    t = time()
    max_e_bits = int(max_e_bits or 32)
    min_e = (2**max_e_bits - 3) if max_e_bits > 3 else 3
    n, e, d, p, q = newkeys(
        bits,
        accurate=accurate,
        poolsize=pool,
        max_e_bits=max_e_bits,
        min_e=min_e,
    )
    info("Duration %ss", time() - t)

    import pprint

    k = dict(n=n, e=e, d=d, p=p, q=q)
    set_int_max_str_digits(1 << 16)
    max_bits = max(v.bit_length() for n, v in k.items())
    k[""] = "{} bits, {} bytes, {}".format(
        max_bits, max_bits // 8, (datetime.utcnow()).strftime("%Y%b%d_%H%M%S")
    )

    with as_sink(output, "w") as out:
        out.write("#")
        for x, v in k.items():
            if x:
                out.write(" {}:{}@{}".format(x, v.bit_length() // 8, v.bit_length()))
        out.write("\n")

        pprint.pprint(k, stream=out)

    if test is not False:
        data = dict(message=platform.encode())
        data["encrypted"] = encrypt(data["message"], n, e)
        data["decrypted"] = decrypt(data["encrypted"], n, d)

        if data["decrypted"] == data["message"]:
            info("test: passed")
        else:
            raise RuntimeError(
                "Test failed message={message!r}, encrypted={encrypted!r}, decrypted={decrypted!r}".format(
                    **data
                )
            )
