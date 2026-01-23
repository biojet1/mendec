import unittest
from math import gcd
from unittest.mock import patch

from mendec.key import calculate_keys_custom_exponent


class TestCalculateKeysCustomExponent(unittest.TestCase):

    # ---- Basic Functionality Tests ----
    @unittest.skip("Enable after testing others")
    def test_generate_random_keys(self):
        """Test generating keys with random e"""
        p, q = 61, 53  # ϕ(n) = 60*52 = 3120
        e, d = calculate_keys_custom_exponent(p, q)

        # Verify basic properties
        self.assertGreaterEqual(e, 65537, "e should be ≥ min_e (65537)")
        self.assertLess(e, 3120, "e should be < ϕ(n)", f"e={e}")
        self.assertEqual((e * d) % ((p - 1) * (q - 1)), 1, "e and d should be inverses")

    # @unittest.skip("Enable after testing others")
    def test_with_custom_e(self):
        """Test providing a valid custom e"""
        p, q = 61, 53
        e, d = calculate_keys_custom_exponent(p, q, e=17)
        self.assertEqual(e, 17)
        self.assertEqual(d, 2753)  # 17^-1 mod 3120

    # ---- Input Validation Tests ----
    # @unittest.skip("Enable after testing others")
    def test_equal_primes(self):
        """Should reject when p == q"""
        with self.assertRaises(ValueError):
            calculate_keys_custom_exponent(7, 7)

    @unittest.skip("Enable after testing others")
    def test_non_prime_inputs(self):
        """Should reject non-prime inputs"""
        with self.assertRaises(ValueError):
            calculate_keys_custom_exponent(8, 13)
        with self.assertRaises(ValueError):
            calculate_keys_custom_exponent(13, 1)

    # ---- Exponent Validation Tests ----
    # @unittest.skip("Enable after testing others")
    def test_invalid_custom_e(self):
        """Should reject invalid custom e values"""
        p, q = 61, 53
        with self.assertRaises(ValueError):
            calculate_keys_custom_exponent(p, q, e=10)  # Not coprime with 3120
        with self.assertRaises(ValueError):
            calculate_keys_custom_exponent(p, q, e=1)  # Too small
        with self.assertRaises(ValueError):
            calculate_keys_custom_exponent(p, q, e=3120)  # Not < ϕ(n)

    # ---- Edge Cases ----
    @unittest.skip("Enable after testing others")
    def test_small_primes(self):
        """Test with smallest valid primes"""
        e, d = calculate_keys_custom_exponent(2, 3)  # ϕ(n) = 1*2 = 2
        self.assertEqual(e, 65537)  # Should use min_e
        self.assertEqual(d, 1)  # 65537 ≡ 1 mod 2

    # @unittest.skip("Enable after testing others")
    def test_min_e_too_large(self):
        """Should reject when min_e ≥ ϕ(n)"""
        with self.assertRaises(ValueError):
            calculate_keys_custom_exponent(3, 5, min_e=8)  # ϕ(n)=2*4=8

    # ---- Randomness Tests ----
    @unittest.skip("Enable after testing others")
    @patch("secrets.randbelow")
    def test_random_e_generation(self, mock_randbelow):
        """Test random e generation logic"""
        mock_randbelow.return_value = 42  # Force randbelow to return 42
        p, q = 61, 53  # ϕ(n)=3120, min_e=65537
        with self.assertRaises(ValueError):
            calculate_keys_custom_exponent(p, q)  # Should fail because 42+65537 > ϕ(n)

        mock_randbelow.return_value = 100
        e, d = calculate_keys_custom_exponent(p, q, min_e=100)
        self.assertEqual(e, 200)  # 100 + min_e(100)

    # @unittest.skip("Enable after testing others")
    def test_exhaustive_search(self):
        """Test behavior when finding e is difficult"""
        # Force gcd check to fail many times
        with patch("math.gcd", side_effect=[2, 2, 2, 2, 2, 1]):
            with self.assertRaises(ValueError):
                calculate_keys_custom_exponent(61, 53, min_e=65537, max_attempts=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
