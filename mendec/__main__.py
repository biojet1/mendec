from ocli import sub, Main
from .cli import decrypt, encrypt, keygen, pick


@sub(
    {
        "decrypt": decrypt.Decrypt,
        "encrypt": encrypt.Encrypt,
        "keygen": keygen.KeyGen,
        "pick": pick.Pick,
    },
    help="select sub command",
    required=True
)
class Top(Main):
    log_level = "INFO"


(__name__ == "__main__") and Top().main()
