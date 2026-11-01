"""Tests for cryptomath.symmetric (run: python3 -m unittest discover -s tests)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cryptomath.symmetric import (  # noqa: E402
    DEFAULT_MODULI, GF2n, aes128_boolean_cost, gold_is_apn, hades_cost, inverse_map,
    is_gold_exponent, is_irreducible_gf2, is_kasami_exponent, lowmc_cost, mimc_cost,
    power_map, power_mult_cost, rasta_cost,
)


def diff_uniformity(f):
    """max over a != 0, b of #{x : f(x ^ a) ^ f(x) = b} (2 = APN)."""
    n = len(f)
    best = 0
    for a in range(1, n):
        cnt = [0] * n
        for x in range(n):
            cnt[f[x ^ a] ^ f[x]] += 1
        best = max(best, max(cnt))
    return best


class TestGF2n(unittest.TestCase):
    def test_default_moduli_irreducible(self):
        for n, m in DEFAULT_MODULI.items():
            self.assertTrue(is_irreducible_gf2(m), n)
        self.assertFalse(is_irreducible_gf2(0b10101))  # (x^2+x+1)^2

    def test_fips197_mul(self):
        F = GF2n(8)
        self.assertEqual(F.mul(0x57, 0x83), 0xC1)
        self.assertEqual(F.mul(0x57, 0x13), 0xFE)
        for a in range(1, 256):
            self.assertEqual(F.mul(a, F.inv(a)), 1)

    def test_cube_apn_odd_n(self):
        for n in (3, 5, 7):
            self.assertEqual(diff_uniformity(power_map(3, n)), 2, n)

    def test_gold_kasami(self):
        self.assertEqual(is_gold_exponent(3, 5), 1)
        self.assertEqual(is_gold_exponent(5, 5), 2)
        self.assertTrue(gold_is_apn(2, 5) and diff_uniformity(power_map(5, 5)) == 2)
        self.assertEqual(is_kasami_exponent(13, 7), 2)   # 2^4 - 2^2 + 1
        self.assertEqual(diff_uniformity(power_map(13, 7)), 2)
        self.assertIsNone(is_gold_exponent(7, 5))

    def test_inverse_map(self):
        inv8 = inverse_map(8)
        self.assertEqual(sorted(inv8), list(range(256)))
        self.assertEqual(diff_uniformity(inv8), 4)
        self.assertEqual(diff_uniformity(inverse_map(5)), 2)   # odd n: inverse is APN


class TestAFCost(unittest.TestCase):
    def test_formulas(self):
        self.assertEqual(power_mult_cost(3), (2, 2))
        self.assertEqual(power_mult_cost(5), (3, 3))
        self.assertEqual(power_mult_cost(7), (4, 3))
        m = mimc_cost(129)
        self.assertEqual(m.nonlinear_ops, 82)          # ceil(129 / log2 3)
        h = hades_cost(3, 8, 57, 5)
        self.assertEqual(h.nonlinear_ops, 3 * 8 + 57)
        self.assertEqual(h.mults, 81 * 3)
        self.assertEqual(rasta_cost(351, 6).mult_depth, 6)
        self.assertEqual(aes128_boolean_cost().mults, 6400)
        self.assertEqual(lowmc_cost(10, 20, 128).mults, 600)



if __name__ == "__main__":
    unittest.main()
