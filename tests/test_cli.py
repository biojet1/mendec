import unittest
from subprocess import call
from hashlib import md5
from tempfile import mkdtemp
from os import chdir, urandom


class Test(unittest.TestCase):
    def shell_ok(self, cmd):
        self.assertEqual(0, call(cmd, shell=True), msg=cmd)

    def shell_fail(self, cmd):
        self.assertNotEqual(0, call(cmd, shell=True), msg=cmd)

    def same_file(self, f1, f2):
        m1, m2 = md5(), md5()
        with open(f1, "rb") as r1:
            m1.update(r1.read())
        with open(f2, "rb") as r2:
            m2.update(r2.read())
        self.assertEqual(m1.hexdigest(), m2.hexdigest(), msg="{} {}".format(f1, f2))

    def test_usage(self):
        self.assertEqual(0, call(r"python3 -m mendec -h", shell=True))
        self.assertEqual(0, call(r"python3 -m mendec encrypt --help", shell=True))

        self.assertEqual(0, call(r"python3 -m mendec decrypt -h", shell=True))
        self.assertEqual(0, call(r"python3 -m mendec pick --help", shell=True))
        self.assertEqual(0, call(r"python3 -m mendec keygen -h", shell=True))
        self.assertNotEqual(0, call(r"python3 -m mendec peck", shell=True))
        self.assertNotEqual(0, call(r"python3 -m mendec decrypt", shell=True))
        self.assertNotEqual(0, call(r"python3 -m mendec encrypt", shell=True))

    def test_example(self):
        tmp = mkdtemp()
        # msg = "Attack at Noon"

        chdir(tmp)
        self.shell_ok("python3 -m mendec keygen --bits 384 --output SECRET_KEY")
        self.shell_ok("python3 -m mendec pick SECRET_KEY 1 KEY1")
        self.shell_ok("python3 -m mendec pick SECRET_KEY 2 KEY2")
        self.shell_ok(
            "printf 'Attack at Noon'" " | python3 -m mendec encrypt -o CYPHER KEY1 -"
        )
        self.shell_ok("python3 -m mendec decrypt KEY2 - < CYPHER")
        self.shell_ok(
            "printf Acknowledge"
            " | python3 -m mendec encrypt KEY2"
            " | python3 -m mendec decrypt KEY1"
        )

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
            " | python3 -m mendec encrypt {1} --short"
            " | python3 -m mendec decrypt {2} --short"
            " | python3 -c 'from sys import stdin, argv; assert(stdin.buffer.read() == argv[1].encode())' {0}"
        )
        self.shell_ok(cmd.format(ascii_letters, "KEY1", "KEY2"))
        self.shell_ok(cmd.format(ascii_letters, "KEY2", "KEY1"))
        self.shell_fail(cmd.format(ascii_letters, "KEY2", "KEY2"))
        self.shell_fail(cmd.format(ascii_letters, "KEY1", "KEY1"))
        self.shell_ok("python3 -m mendec encrypt KEY1 MSG -o ENC1")
        self.shell_ok("python3 -m mendec decrypt KEY2 ENC1 -o DEC1")
        self.same_file("MSG", "DEC1")
        self.shell_fail("python3 -m mendec decrypt KEY1 ENC1 -o DEC1")
        self.shell_ok("python3 -m mendec encrypt KEY2 MSG -o - > ENC2")
        self.shell_ok("python3 -m mendec decrypt KEY1 ENC2 -o DEC2")
        self.same_file("MSG", "DEC2")
        self.shell_fail("python3 -m mendec decrypt KEY2 ENC2 -o DEC2")


if __name__ == "__main__":
    unittest.main()
