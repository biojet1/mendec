from pathlib import Path
import unittest
from subprocess import call
from hashlib import md5
from tempfile import mkdtemp
from os import chdir, urandom


class Test(unittest.TestCase):
    def shell_ok(self, cmd, **kwargs):
        self.assertEqual(0, call(cmd, shell=True, **kwargs), msg=cmd)

    def shell_fail(self, cmd):
        self.assertNotEqual(0, call(cmd, shell=True), msg=cmd)

    def same_file(self, f1, f2, _not=False):
        m1, m2 = md5(), md5()
        with open(f1, "rb") as r1:
            m1.update(r1.read())
        with open(f2, "rb") as r2:
            m2.update(r2.read())
        d1, d2 = m1.hexdigest(), m2.hexdigest()
        if _not:
            self.assertNotEqual(d1, d2, msg="{} {}".format(f1, f2))
        else:
            self.assertEqual(d1, d2, msg="{} {}".format(f1, f2))

    def different_file(self, f1, f2, _not=False):
        return self.same_file(f1, f2, _not=True)

    # def test_usage(self):
    #     self.assertEqual(0, call(r"python3 -m mendec -h", shell=True))
    #     self.assertEqual(0, call(r"python3 -m mendec encrypt --help", shell=True))

    #     self.assertEqual(0, call(r"python3 -m mendec decrypt -h", shell=True))
    #     self.assertEqual(0, call(r"python3 -m mendec pick --help", shell=True))
    #     self.assertEqual(0, call(r"python3 -m mendec keygen -h", shell=True))
    #     self.assertNotEqual(0, call(r"python3 -m mendec peck", shell=True))
    #     self.assertNotEqual(0, call(r"python3 -m mendec decrypt", shell=True))
    #     self.assertNotEqual(0, call(r"python3 -m mendec encrypt", shell=True))

    # def test_example(self):
    #     tmp = mkdtemp()
    #     # msg = "Attack at Noon"

    #     chdir(tmp)
    #     self.shell_ok("python3 -m mendec keygen --bits 384 --output SECRET_KEY")
    #     self.shell_ok("python3 -m mendec pick SECRET_KEY 1 KEY1")
    #     self.shell_ok("python3 -m mendec pick SECRET_KEY 2 KEY2")
    #     self.shell_ok(
    #         "printf 'Attack at Noon'" " | python3 -m mendec encrypt -o CYPHER KEY1 -"
    #     )
    #     self.shell_ok("python3 -m mendec decrypt KEY2 - < CYPHER")
    #     self.shell_ok(
    #         "printf Acknowledge"
    #         " | python3 -m mendec encrypt KEY2"
    #         " | python3 -m mendec decrypt KEY1"
    #     )
    def test_script(self):

        key = pwd.joinpath("tests/k384.key")
        lic = pwd.joinpath("LICENSE")
        tmp = mkdtemp()
        self.shell_ok(f"python3 -m mendec script {key} b k384E k384D", cwd=tmp)
        self.shell_ok(
            f"cat {lic} | python3 k384E > _enc ; cat _enc | python3 k384D > _dec ; stat {lic} _dec _enc |  grep -P 'File|Size'",
            cwd=tmp,
        )
        self.same_file(lic, f"{tmp}/_dec")

    def test_enc_dec(self):
        from base64 import b64encode
        from string import ascii_letters

        tmp = mkdtemp()

        chdir(tmp)
        with open("MSG", "wb") as h:
            h.write(b64encode(urandom(1 * 1024 * 1024)))

        self.shell_ok("python3 -m mendec keygen -B96 -p4 -o KEY")
        self.shell_ok("python3 -m mendec pick KEY 1 KEY1")
        self.shell_ok("python3 -m mendec pick KEY 2 KEY2")
        cmd = (
            "echo -n {0}"
            " | python3 -m mendec encrypt {1}"
            " | python3 -m mendec decrypt {2}"
            " | python3 -c 'from sys import stdin, argv; assert(stdin.buffer.read() == argv[1].encode())' {0}"
        )
        self.shell_ok(cmd.format(ascii_letters, "KEY1", "KEY2"))
        self.shell_ok(cmd.format(ascii_letters, "KEY2", "KEY1"))
        self.shell_fail(cmd.format(ascii_letters, "KEY2", "KEY2"))
        self.shell_fail(cmd.format(ascii_letters, "KEY1", "KEY1"))
        self.different_file("KEY2", "KEY1")
        self.shell_ok("ls -lAsh; cat KEY1")
        self.shell_ok("python3 -m mendec encrypt KEY1 MSG ENC1")
        self.shell_ok("python3 -m mendec decrypt KEY2 ENC1 DEC1")
        self.same_file("MSG", "DEC1")
        # self.shell_fail("python3 -m mendec decrypt KEY1 ENC1 DEC1")
        self.shell_ok("python3 -m mendec encrypt KEY2 MSG - > ENC2")
        self.shell_ok("python3 -m mendec decrypt KEY1 ENC2 DEC2")
        self.same_file("MSG", "DEC2")
        # self.shell_fail("python3 -m mendec decrypt KEY2 ENC2 DEC2")
        ## script

        # self.shell_ok("cat LICENSE | tee /tmp/_txt | .vscode/k384E - - | tee /tmp/_enc | .vscode/k384D | tee /tmp/_dec | md5sum - /tmp/_txt /tmp/_dec ; stat /tmp/_txt /tmp/_dec /tmp/_enc |  grep -P 'File|Size'")


pwd = Path.cwd()
if __name__ == "__main__":
    unittest.main()
