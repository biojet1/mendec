import unittest


class Test(unittest.TestCase):
    def test_varint(self):
        from mendec.varint import encode_stream, decode_stream
        from random import SystemRandom
        from io import BytesIO

        random = SystemRandom()

        enb = BytesIO()

        bits = (8, 4 * 8, 444 * 8, 4444 * 8)

        ints = [random.getrandbits(b) for b in bits]
        for i in ints:
            encode_stream(enb, i)

        deb = BytesIO(enb.getvalue())
        for i in ints:
            j = decode_stream(deb)
            self.assertEqual(i, j)
        self.assertEqual(deb.read(), b"")

        # print(usage(x))

    def test_enc_dec(self):
        from os import urandom
        from mendec.message import encrypt, decrypt
        from mendec.key import newkeys

        def try1(bits, accurate, pool):
            n, e, d = newkeys(bits, accurate, pool)

            bits_max = n.bit_length()
            q, r = divmod(bits_max - 1, 8)
            bytes_max = q if q > 0 else q + 1
            for s in (bytes_max, bytes_max // 4, bytes_max // 3, bytes_max // 2, 1):
                message = urandom(s)
                message = message.strip(b"\x00")
                if not message:
                    message = b"\x42"

                encrypted = encrypt(message, n, e)
                decrypted = decrypt(encrypted, n, d)
                self.assertEqual(decrypted, message, s)
                encrypted = encrypt(message, n, d)
                decrypted = decrypt(encrypted, n, e)
                self.assertEqual(decrypted, message, s)
                if len(message) > 2:
                    encrypted = encrypt(message, n, d)
                    decrypted = decrypt(encrypted, n, d)
                    self.assertNotEqual(decrypted, message, s)
                    encrypted = encrypt(message, n, e)
                    decrypted = decrypt(encrypted, n, e)
                    self.assertNotEqual(decrypted, message, s)

        for bits in (64, 96, 256):
            for accurate in (True, False):
                for pool in (1, 2, 3):
                    try1(bits, accurate, pool)

    def test_utils(self):
        from mendec.utils import byte_size, int2bytes

        self.assertEqual(byte_size(0), 1)
        self.assertEqual(byte_size(0xFF), 1)
        self.assertEqual(byte_size(0xFF + 1), 2)

        with self.assertRaisesRegex(ValueError, "Negative.+can.+t.+"):
            int2bytes(-1)
        self.assertEqual(int2bytes(0), b"\x00")

    def test_prime(self):
        from mendec.prime import gcd, is_prime, are_relatively_prime

        self.assertEqual(gcd(48, 180), 12)

        for n in [1, 4, 6, 8, 9]:
            self.assertEqual(is_prime(n), False, f"is_prime({n})")
        for n in [2, 3, 5, 7]:
            self.assertEqual(is_prime(n), True, f"is_prime({n})")
        self.assertEqual(are_relatively_prime(7, 20), True)
        self.assertEqual(are_relatively_prime(10, 8), False)


if __name__ == "__main__":
    unittest.main()
