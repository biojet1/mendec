import unittest
from subprocess import call


class Test(unittest.TestCase):
    def test_usage(self):

        self.assertEqual(0, call(r"python -m mendec -h", shell=True))
        self.assertEqual(0, call(r"python -m mendec encrypt --help", shell=True))
        self.assertEqual(0, call(r"python -m mendec decrypt -h", shell=True))
        self.assertEqual(0, call(r"python -m mendec pick --help", shell=True))
        self.assertEqual(0, call(r"python -m mendec keygen -h", shell=True))
        self.assertNotEqual(0, call(r"python -m mendec", shell=True))
        self.assertNotEqual(0, call(r"python -m mendec decrypt", shell=True))
        self.assertNotEqual(0, call(r"python -m mendec encrypt", shell=True))

    def check_shell(self, cmd):
        self.assertEqual(0, call(cmd, shell=True), msg=cmd)

    def test_enc_dec(self):
        from os import chdir, urandom
        from tempfile import mkdtemp
        from hashlib import md5
        from base64 import b64encode
        from string import ascii_letters

        tmp = mkdtemp()

        chdir(tmp)
        with open("MSG", "wb") as h:
            h.write(b64encode(urandom(128 * 1024)))

        self.check_shell("python -m mendec keygen -B96 -p4 -o KEY")
        self.check_shell("python -m mendec pick KEY 1 KEY1")
        self.check_shell("python -m mendec pick KEY 2 KEY2")
        cmd = (
            "printf {0}"
            " | python -m mendec.cli.encrypt {1} --short"
            " | python -m mendec.cli.decrypt {2} --short"
            r""" | python -c 'import sys; assert(sys.stdin.read() == "{0}")'"""
        )
        self.check_shell(cmd.format(ascii_letters, "KEY1", "KEY2"))
        self.check_shell(cmd.format(ascii_letters, "KEY2", "KEY1"))
        self.check_shell("python -m mendec encrypt --no-short KEY1 MSG -o ENC")
        self.check_shell("python -m mendec decrypt --no-short KEY2 ENC -o DEC")
        msg, dec = md5(), md5()
        msg.update(open("MSG", "rb").read())
        dec.update(open("DEC", "rb").read())

        self.assertEqual(dec.hexdigest(), msg.hexdigest())
