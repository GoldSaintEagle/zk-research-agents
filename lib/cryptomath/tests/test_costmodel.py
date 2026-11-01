import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sympy as sp  # noqa: E402

from cryptomath.costmodel import (  # noqa: E402
    BFLY, GADD, HASH, MSM, MSM_PTS, MUL, NTT, PAIR, SC_ROUND, SC_TERM, SMULT, CostFormula,
    Counter, Traced, compare, count, count_fri_commit, count_kzg_open, count_msm,
    count_sumcheck_prover, counted, fri_commit_formula, fri_fold_formula, fri_fold_hashes,
    fri_query_formula, fri_query_hashes, karatsuba_formula, kzg_open_formula, kzg_verify_formula,
    merkle_formula, merkle_hashes, merkle_opening_formula, merkle_opening_nodes,
    merkle_pruned_nodes, msm_formula, msm_group_adds, ntt_butterflies, ntt_formula,
    pippenger_window, schoolbook_formula, sumcheck_formula, sumcheck_terms,
)


@counted(NTT)
def fake_ntt(v):
    return v


def schoolbook(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            count("field_mult")
            out[i + j] += x * y
    return out


def karatsuba(a, b):
    n = len(a)
    if n == 1:
        count("field_mult")
        return [a[0] * b[0]]
    h = n // 2
    a0, a1, b0, b1 = a[:h], a[h:], b[:h], b[h:]
    z0 = karatsuba(a0, b0)
    z2 = karatsuba(a1, b1)
    z1 = karatsuba([x + y for x, y in zip(a0, a1)], [x + y for x, y in zip(b0, b1)])
    z1 = [m - p - q for m, p, q in zip(z1, z0, z2)]
    out = [0] * (2 * n - 1)
    for i, v in enumerate(z0):
        out[i] += v
    for i, v in enumerate(z1):
        out[i + h] += v
    for i, v in enumerate(z2):
        out[i + 2 * h] += v
    return out


class TestCounter(unittest.TestCase):
    def test_nesting_and_decorator(self):
        with Counter("outer") as outer:
            fake_ntt([1])
            with Counter("inner") as inner:
                fake_ntt([1])
                count(HASH, 3)
        self.assertEqual(outer[NTT], 2)
        self.assertEqual(inner[NTT], 1)
        self.assertEqual(outer[HASH], 3)
        count(HASH)  # no active counter: no-op
        self.assertEqual(outer[HASH], 3)

    def test_traced(self):
        with Counter() as c:
            x = Traced(3)
            y = x * x * x + x * 2 + 1
        self.assertEqual(y.value, 34)
        self.assertEqual(c[MUL], 2)
        self.assertEqual(c[SMULT], 1)
        self.assertEqual(y.depth, 2)
        self.assertEqual(c.max_depth, 2)
        with Counter() as c2:
            z = Traced(2) ** 13
        self.assertEqual(z.value, 2 ** 13)
        self.assertEqual(z.depth, 4)
        # Poseidon-style S-box x^5 + 7x: 3 nonlinear mults = 3 R1CS constraints
        with Counter() as c3:
            x = Traced(3)
            y = x ** 5 + 7 * x
        self.assertEqual((c3[MUL], y.depth, y.value), (3, 3, 264))

    def test_compare(self):
        a = list(range(1, 9))
        b = list(range(2, 10))
        rep = compare(schoolbook, karatsuba, a, b, names=("school", "kara"),
                      weights={"field_mult": 1.0})
        self.assertTrue(rep["equal_outputs"])
        self.assertEqual(rep["counts"]["school"]["field_mult"], 64)
        self.assertEqual(rep["counts"]["kara"]["field_mult"], 27)
        self.assertIn("| school |", rep["report"])


class TestFormulas(unittest.TestCase):
    def test_eval_and_crossover(self):
        s, k = schoolbook_formula(), karatsuba_formula()
        self.assertEqual(k.crossover(s, "n", weights={"field_mult": 1}), 2)
        both = s + k
        self.assertIn("field_mult", both.terms)
        n = sp.Symbol("n", positive=True)
        f = CostFormula({MUL: n ** 2 + 5 * n})
        self.assertEqual(sp.simplify(f.leading("n", {MUL: 1}) - n ** 2), 0)
        # MSM is cheaper per point than N scalar multiplications (~1.5 b additions each) once N grows
        ms = msm_formula().evaluate(N=2 ** 16, b=254, c=14)
        self.assertLess(ms[GADD], 2 ** 16 * 1.5 * 254 / 5)

    def test_zk_formulas_match_zkops(self):
        for N in (2 ** 4, 2 ** 10, 2 ** 16):
            c = pippenger_window(N)
            self.assertEqual(msm_formula().evaluate(N=N, b=254, c=c)[GADD], msm_group_adds(N, 254))
            self.assertEqual(ntt_formula().evaluate(N=N)[BFLY], ntt_butterflies(N))
            self.assertEqual(merkle_formula().evaluate(L=N)[HASH], merkle_hashes(N))
            self.assertEqual(merkle_opening_formula().evaluate(L=N, q=7)[HASH],
                             merkle_opening_nodes(N.bit_length() - 1, 7))
            for rho in (2, 4, 8):
                with Counter() as cf:
                    count_fri_commit(N, rho)
                ev = fri_commit_formula().evaluate(N=N, rho=rho)
                self.assertEqual((ev[NTT], ev[BFLY], ev[HASH]), (cf[NTT], cf[BFLY], cf[HASH]))
                self.assertEqual(fri_fold_formula().evaluate(N=N, rho=rho)[HASH], fri_fold_hashes(N, rho))
                self.assertEqual(fri_query_formula().evaluate(N=N, rho=rho, q=30)[HASH],
                                 fri_query_hashes(N, rho, 30))
            with Counter() as ck:
                count_kzg_open(N, 255)
            ev = kzg_open_formula().evaluate(N=N, b=255, c=pippenger_window(N - 1))
            self.assertEqual((ev[MSM_PTS], ev[GADD]), (ck[MSM_PTS], ck[GADD]))
        self.assertEqual(kzg_verify_formula().evaluate()[PAIR], 2)
        for v, d in ((1, 1), (5, 2), (12, 3)):
            ev = sumcheck_formula().evaluate(v=v, d=d)
            with Counter() as cs:
                count_sumcheck_prover(v, d)
            self.assertEqual((ev[SC_ROUND], ev[SC_TERM]), (cs[SC_ROUND], cs[SC_TERM]))
            self.assertEqual(ev[SC_TERM], sumcheck_terms(v, d))

    def test_hand_counts(self):
        # by hand: N = 8 NTT has 3 layers of 4 butterflies; 8 leaves -> 8 + 4 + 2 + 1 = 15 hashes
        self.assertEqual(ntt_butterflies(8), 12)
        self.assertEqual(merkle_hashes(8), 15)
        # v = 3, d = 2: 3 * (4 + 2 + 1) = 21 evaluations of the summand
        self.assertEqual(sumcheck_terms(3, 2), 21)
        # MSM N = 16, b = 8, window 2: 4 windows * (16 + 8) = 96 additions
        self.assertEqual(msm_group_adds(16, 8), 96)
        with Counter() as c:
            count_msm(16, 8)
        self.assertEqual((c[MSM], c[MSM_PTS], c[GADD]), (1, 16, 96))
        # pruning: opening leaves {0, 1} of 8 shares the path above them -> 2 nodes instead of 6
        self.assertEqual(merkle_pruned_nodes(3, {0, 1}), 2)
        self.assertEqual(merkle_pruned_nodes(3, {0, 7}), 4)
        # FRI N = 4, rho = 2: fold layers over 4 and 2 leaves -> 7 + 3 hashes; queries walk 3 + 2 + 1 nodes
        self.assertEqual(fri_fold_hashes(4, 2), 10)
        self.assertEqual(fri_query_hashes(4, 2, 1), 6)

if __name__ == "__main__":
    unittest.main()
