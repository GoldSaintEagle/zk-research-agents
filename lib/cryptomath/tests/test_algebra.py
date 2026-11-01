import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptomath.algebra import (  # noqa: E402
    GF, CyclotomicNTT, PolyRing, carmichael_lambda, cosets, crt, cyclotomic_poly,
    dft_bluestein, dft_naive, euler_phi, factorint, find_ntt_prime, find_ntt_primes,
    intt_cyclic, intt_negacyclic, is_irreducible, is_prime, mult_order, negacyclic_mul_ntt,
    ntt_cyclic, ntt_negacyclic, poly_divmod, poly_eval, poly_mul, primitive_root,
    root_of_unity, subgroup_generated, unit_group_generators, units,
)


class TestNumberTheory(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(factorint(360), {2: 3, 3: 2, 5: 1})
        self.assertEqual(euler_phi(105), 48)
        self.assertEqual(carmichael_lambda(16), 4)
        self.assertEqual(mult_order(2, 7), 3)
        self.assertEqual(mult_order(2, 31), 5)
        self.assertTrue(is_prime(2 ** 61 - 1))
        self.assertFalse(is_prime(561))
        self.assertEqual(primitive_root(7), 3)
        x, M = crt([2, 3, 2], [3, 5, 7])
        self.assertEqual((x, M), (23, 105))

    def test_unit_group(self):
        for m in (8, 15, 16, 40, 63, 64):
            gens = unit_group_generators(m)
            H = subgroup_generated([g for g, _ in gens], m)
            self.assertEqual(H, units(m))
            prod = 1
            for _, o in gens:
                prod *= o
            self.assertEqual(prod, euler_phi(m))
        cs = cosets(subgroup_generated([2], 31), 31)   # <2> in (Z/31)^*, order 5
        self.assertEqual(len(cs), 6)
        self.assertTrue(all(len(c) == 5 for c in cs))

    def test_ntt_primes(self):
        for q in find_ntt_primes(30, 128, 3):
            self.assertTrue(is_prime(q) and q % 128 == 1 and q < 2 ** 30)
        q = find_ntt_prime(20, 64)
        w = root_of_unity(64, q)
        self.assertEqual(pow(w, 64, q), 1)
        self.assertNotEqual(pow(w, 32, q), 1)


class TestPoly(unittest.TestCase):
    def test_cyclotomic(self):
        self.assertEqual(cyclotomic_poly(1), [-1, 1])
        self.assertEqual(cyclotomic_poly(8), [1, 0, 0, 0, 1])
        self.assertEqual(cyclotomic_poly(12), [1, 0, -1, 0, 1])
        # Phi_105 is the first with a coefficient -2
        self.assertIn(-2, cyclotomic_poly(105))
        for m in (9, 20, 21, 30):
            self.assertEqual(len(cyclotomic_poly(m)) - 1, euler_phi(m))

    def test_divmod(self):
        a = [random.randrange(-50, 50) for _ in range(12)]
        b = [3, 0, 1, 1]
        q, r = poly_divmod(a, b)
        back = poly_mul(q, b)
        back = [x + (r[i] if i < len(r) else 0) for i, x in enumerate(back + [0] * (len(a) - len(back)))]
        self.assertEqual(back[: len(a)], a)

    def test_ring_and_automorphisms(self):
        for m, q in ((16, 97), (15, 31), (12, 13)):
            R = PolyRing(m=m, q=q)
            a, b = R.uniform(), R.uniform()
            # automorphisms are ring homomorphisms and compose correctly
            for k in units(m)[:4]:
                self.assertTrue(all(R.automorphism(R.mul(a, b), k) == R.mul(R.automorphism(a, k), R.automorphism(b, k))))
            k1, k2 = units(m)[1], units(m)[-1]
            self.assertTrue(all(R.automorphism(R.automorphism(a, k1), k2) == R.automorphism(a, k1 * k2 % m)))
            # X^m = 1
            self.assertTrue(all(R.pow(R.monomial(1), m) == R.one()))

    def test_negacyclic_matches_generic(self):
        R1 = PolyRing(m=32, q=257)
        R2 = PolyRing(modulus=[1] + [0] * 15 + [1], q=257)
        a, b = R1.uniform(), R1.uniform()
        self.assertTrue(all(R1.mul(a, b) == R2._reduce_full(R2._full_product(a, b)) % 257))


class TestFiniteField(unittest.TestCase):
    def test_gf256(self):
        F = GF(2, 8, modulus=[1, 1, 0, 1, 1, 0, 0, 0, 1])
        a = F.from_int(0x53)
        self.assertEqual((a * a.inverse()).to_int(), 1)
        self.assertEqual(a.inverse().to_int(), 0xCA)  # classic AES example
        g = F.primitive_element()
        self.assertEqual(len({(g ** i).to_int() for i in range(255)}), 255)

    def test_prime_power_fields(self):
        for p, k in ((3, 2), (5, 3), (7, 2)):
            F = GF(p, k)
            self.assertTrue(is_irreducible(F.modulus, p))
            x = F.random(random.Random(1))
            self.assertEqual(x ** F.order, x)  # Frobenius^k = id
            mp = F.gen.minpoly()
            self.assertEqual(mp, F.modulus)


class TestNTT(unittest.TestCase):
    def test_cyclic_and_negacyclic(self):
        q = find_ntt_prime(30, 128)
        a = [random.randrange(q) for _ in range(64)]
        self.assertEqual(intt_cyclic(ntt_cyclic(a, q), q), a)
        self.assertEqual(intt_negacyclic(ntt_negacyclic(a, q), q), a)
        w = root_of_unity(64, q)
        self.assertEqual(ntt_cyclic(a, q, w), dft_naive(a, q, w))
        b = [random.randrange(q) for _ in range(64)]
        R = PolyRing(m=128, q=q)
        self.assertEqual(negacyclic_mul_ntt(a, b, q), [int(x) for x in R.mul(a, b)])

    def test_bluestein(self):
        n = 15
        q = find_ntt_prime(40, 2 * n * 64)  # also admits the power-of-two convolution
        w = root_of_unity(n, q)
        a = [random.randrange(q) for _ in range(n)]
        self.assertEqual(dft_bluestein(a, q, w), dft_naive(a, q, w))

    def test_cyclotomic_ntt(self):
        for m in (21, 16, 15):
            q = find_ntt_prime(30, 2 * m)
            C = CyclotomicNTT(m, q)
            R = PolyRing(m=m, q=q)
            x = [random.randrange(q) for _ in range(C.n)]
            y = [random.randrange(q) for _ in range(C.n)]
            self.assertEqual(C.inverse(C.forward(x)), x)
            self.assertEqual([u * v % q for u, v in zip(C.forward(x), C.forward(y))], C.forward([int(c) for c in R.mul(x, y)]))


if __name__ == "__main__":
    unittest.main()
