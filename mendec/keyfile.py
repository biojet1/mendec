from ast import literal_eval
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict


def find_key(key="main.key"):
    from pathlib import Path
    from os import environ

    def places():
        if v := environ.get("XDG_CONFIG_HOME"):
            yield Path(v) / "mendec"
        if v := environ.get("XDG_CONFIG_DIRS"):
            for u in v.split(":"):
                if u:
                    yield Path(u) / "mendec"
        yield Path.home() / ".config" / "mendec"
        yield Path.home() / ".mendec"

    s = Path(key)

    if s.exists():
        return s
    elif s.is_absolute():
        pass
    else:
        for d in places():
            if d.is_dir():
                k = d / s
                if k.is_file():
                    return k
                k = d / f"{s}.key"
                if k.is_file():
                    return k
    raise FileNotFoundError(key)


def parse_keyfile(path):
    # type: (str) -> Dict[str, int]
    with open(path, "rb") as r:
        d = r.read()
        if d.startswith(b"-----BEGIN PRIV") or d.startswith(b"-----BEGIN RSA PRIVATE"):
            pem = 1
        elif d.startswith(b"-----BEGIN PUBL"):
            pem = 2

        else:
            pem = 0
        # print(h, pem)
        if pem > 0:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa

            if pem == 1:
                pk = serialization.load_pem_private_key(d, None)
                return {
                    "e": pk.public_key().public_numbers().e,
                    "n": pk.public_key().public_numbers().n,
                    "d": pk.private_numbers().d,
                }
            else:
                pk = serialization.load_pem_public_key(d, None)
                return {
                    "e": pk.public_numbers().e,
                    "n": pk.public_numbers().n,
                }
        else:
            return parse_key(d.decode())


def parse_key(text):
    # type: (str) -> Dict[str, int]
    return literal_eval(text)


def to_pem(nums={}, dest="private_key.pem"):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    # Your existing integer values
    p = nums["p"]
    q = nums["q"]
    n = nums["n"]
    e = nums["e"]
    d = nums["d"]

    # 1. Calculate the CRT (Chinese Remainder Theorem) components
    # These are required by the RSAPrivateNumbers structure
    dmp1 = d % (p - 1)
    dmq1 = d % (q - 1)
    iqmp = pow(q, -1, p)

    # 2. Create the Private Numbers object
    private_numbers = rsa.RSAPrivateNumbers(
        p=p,
        q=q,
        d=d,
        dmp1=dmp1,
        dmq1=dmq1,
        iqmp=iqmp,
        public_numbers=rsa.RSAPublicNumbers(e, n),
    )

    # 3. Create the key object
    key = private_numbers.private_key()

    # 4. Serialize to PEM format
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
        encryption_algorithm=serialization.NoEncryption(),
    )

    # 5. Write to file
    with open(dest, "wb") as f:
        f.write(pem)

    # print("PEM file created successfully.")
