from ast import literal_eval
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict


def find_key(key):
    # type: (str) -> str
    from os.path import expanduser, isdir, join, isfile, exists

    def dirs():
        yield "/dev/shm/.keys"
        yield expanduser("~/.keys")
        yield "/usr/share/.keys"

    if exists(key):
        return key
    for d in dirs():
        if isdir(d):
            k = join(d, key)
            if isfile(k):
                return k
            k = join(d, f"{key}.key")
            if isfile(k):
                return k
    raise FileNotFoundError(key)


# def parse_keyfile(path):
#     # type: (str) -> Dict[str, int]
#     with open(path, "r") as r:
#         return parse_key(r.read())


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


# def to_pem2(nums={}, dest="private_key.pem"):
#     from cryptography.hazmat.primitives.asymmetric import rsa
#     from cryptography.hazmat.primitives import serialization

#     # Your RSA components
#     p = nums["p"]
#     q = nums["q"]
#     n = nums["n"]
#     e = nums["e"]
#     d = nums["d"]

#     # Create private key
#     private_key = rsa.RSAPrivateNumbers(
#         p=p,
#         q=q,
#         d=d,
#         dmp1=rsa.rsa_crt_dmp1(d, p),  # d mod (p-1)
#         dmq1=rsa.rsa_crt_dmq1(d, q),  # d mod (q-1)
#         iqmp=rsa.rsa_crt_iqmp(p, q),  # q^(-1) mod p
#         public_numbers=rsa.RSAPublicNumbers(e=e, n=n),
#     ).private_key()

#     # Convert to PEM format
#     private_pem = private_key.private_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PrivateFormat.PKCS8,
#         encryption_algorithm=serialization.NoEncryption(),
#     )

#     # Save to file
#     with open(dest, "wb") as f:
#         f.write(private_pem)

#     # # Get public key PEM
#     # public_key = private_key.public_key()
#     # public_pem = public_key.public_bytes(
#     #     encoding=serialization.Encoding.PEM,
#     #     format=serialization.PublicFormat.SubjectPublicKeyInfo,
#     # )

#     # with open("public_key.pem", "wb") as f:
#     #     f.write(public_pem)

#     # print("Private key PEM:")
#     # print(private_pem.decode())
#     # print("\nPublic key PEM:")
#     # print(public_pem.decode())
