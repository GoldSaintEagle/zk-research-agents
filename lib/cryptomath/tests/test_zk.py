"""Tests for cryptomath.zk: completeness, empirical soundness against the theoretical bounds,
Merkle binding / openings, FRI on honest and tampered proofs, and counts against hand computations."""
import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptomath.algebra import ntt_cyclic  # noqa: E402
from cryptomath.costmodel import (  # noqa: E402
    BFLY, GADD, MSM_PTS, PAIR, SC_ROUND, SC_TERM, Counter, msm_group_adds, ntt_butterflies, sumcheck_terms,
)
from cryptomath.zk import field, fri, kzg, merkle, mle, plonk, plonkish, r1cs, sumcheck  # noqa: E402
from cryptomath.zk.field import GOLDILOCKS, P17, P97  # noqa: E402


def binom_upper(p_hat_bound: float, trials: int, z: float = 4.0) -> float:
    """Bound + z standard deviations: an empirical rate above this contradicts the bound."""
    return p_hat_bound + z * math.sqrt(max(p_hat_bound * (1 - p_hat_bound), 1e-12) / trials)


class TestField(unittest.TestCase):
    def test_roots_and_interpolation(self):
        for p, n in ((P17, 16), (P97, 32), (GOLDILOCKS, 2 ** 20)):
            w = field.root_of_unity(n, p)
            self.assertEqual(pow(w, n, p), 1)
            self.assertNotEqual(pow(w, n // 2, p), 1)
        rng = random.Random(1)
        f = [rng.randrange(P97) for _ in range(5)]
        xs = list(range(10, 15))
        self.assertEqual(field.interpolate(xs, [field.poly_eval(f, x, P97) for x in xs], P97), f)
        ys = [field.poly_eval(f[:3], x, P97) for x in range(3)]
        self.assertEqual(field.interpolate_eval(ys, 50, P97), field.poly_eval(f[:3], 50, P97))
        q, rem = field.poly_divmod_linear(f, 7, P97)
        self.assertEqual(rem, field.poly_eval(f, 7, P97))
        self.assertEqual(field.poly_add(field.poly_mul(q, [-7 % P97, 1], P97), [rem], P97), f)
        xs = [3, 5, 11]
        self.assertEqual([a * b % P97 for a, b in zip(xs, field.batch_inv(xs, P97))], [1, 1, 1])


class TestMLE(unittest.TestCase):
    def test_extension_and_eq(self):
        rng = random.Random(2)
        for p in (P17, P97, GOLDILOCKS):
            for v in (1, 3, 5):
                t = [rng.randrange(p) for _ in range(2 ** v)]
                for i in range(2 ** v):
                    self.assertEqual(mle.mle_eval(t, mle.bits(i, v), p), t[i])
                r = [rng.randrange(p) for _ in range(v)]
                self.assertEqual(mle.mle_eval(t, r, p), mle.mle_eval_lagrange(t, r, p))
                et = mle.eq_table(r, p)
                self.assertEqual(sum(et) % p, 1)       # sum_b eq(b, r) = 1
                self.assertEqual(et, [mle.eq(mle.bits(i, v), r, p) for i in range(2 ** v)])

    def test_hand_example(self):
        # f = (1, 2, 3, 4) on (x1, x2) = 00, 01, 10, 11: f~ = 1 + x2 + 2 x1, so f~(5, 7) = 18 = 1 mod 17
        self.assertEqual(mle.mle_eval([1, 2, 3, 4], [5, 7], P17), 18 % 17)


class TestSumcheck(unittest.TestCase):
    def test_completeness_and_counts(self):
        rng = random.Random(3)
        for p in (P17, P97, GOLDILOCKS):
            for v, d in ((1, 1), (3, 2), (5, 3)):
                tabs = [[rng.randrange(p) for _ in range(2 ** v)] for _ in range(d)]
                with Counter() as c:
                    res = sumcheck.run(tabs, p, rng)
                self.assertTrue(res["accepted"])
                self.assertEqual(res["claim"], sumcheck.true_sum(tabs, p))
                self.assertEqual((c[SC_ROUND], c[SC_TERM]), (v, sumcheck_terms(v, d)))

    def test_custom_combine(self):
        # Spartan-style summand eq(x, tau) * (a(x) b(x) - c(x)): degree 3, sum 0 iff the rows satisfy a*b = c
        p, rng = P97, random.Random(4)
        v = 3
        a = [rng.randrange(p) for _ in range(8)]
        b = [rng.randrange(p) for _ in range(8)]
        c = [x * y % p for x, y in zip(a, b)]
        e = mle.eq_table([rng.randrange(p) for _ in range(v)], p)
        comb = lambda t: t[0] * (t[1] * t[2] - t[3])
        res = sumcheck.run([e, a, b, c], p, rng, combine=comb, degree=3)
        self.assertTrue(res["accepted"] and res["claim"] == 0)

    def test_empirical_soundness(self):
        """The cheating prover wins w.p. 1 - (1 - d/p)^v <= v d / p; measure it."""
        trials = 3000
        for p, v, d in ((P17, 2, 1), (P97, 3, 2), (P97, 4, 3)):
            rng = random.Random(100 + v)
            tabs = [[rng.randrange(p) for _ in range(2 ** v)] for _ in range(d)]
            wins = sum(sumcheck.run(tabs, p, rng, sumcheck.CheatingProver(tabs, p, delta=5, rng=rng))["accepted"]
                       for _ in range(trials))
            rate, bound = wins / trials, sumcheck.soundness_bound(v, d, p)
            exact = 1 - (1 - d / p) ** v
            self.assertLessEqual(rate, binom_upper(bound, trials), (p, v, d, rate, bound))
            self.assertGreater(rate, exact / 2, "the cheater should be near-optimal, else the test is vacuous")
        # over Goldilocks the same cheater essentially never wins
        rng = random.Random(9)
        tabs = [[rng.randrange(GOLDILOCKS) for _ in range(8)] for _ in range(2)]
        self.assertFalse(any(sumcheck.run(tabs, GOLDILOCKS, rng, sumcheck.CheatingProver(tabs, GOLDILOCKS, rng=rng))
                             ["accepted"] for _ in range(50)))

    def test_fiat_shamir(self):
        rng = random.Random(5)
        p = P97
        tabs = [[rng.randrange(p) for _ in range(16)] for _ in range(2)]
        proof = sumcheck.prove_fs(tabs, p)
        self.assertTrue(sumcheck.verify_fs(proof, tabs, p))
        self.assertEqual(sumcheck.prove_fs(tabs, p), proof)          # deterministic
        bad = dict(proof, claim=(proof["claim"] + 1) % p)
        self.assertFalse(sumcheck.verify_fs(bad, tabs, p))
        msgs = [m[:] for m in proof["messages"]]
        msgs[1][0] = (msgs[1][0] + 1) % p
        msgs[1][1] = (msgs[1][1] - 1) % p                           # keeps s(0) + s(1), changes s
        self.assertFalse(sumcheck.verify_fs(dict(proof, messages=msgs), tabs, p))
        self.assertFalse(sumcheck.verify_fs(proof, tabs, p, label=b"other-domain"))
        # a cheating prover made non-interactive: wins only if a hashed challenge hits a root
        wins = 0
        for s in range(300):
            ch = sumcheck.CheatingProver(tabs, p, delta=3, rng=random.Random(s))
            wins += sumcheck.verify_fs(sumcheck.prove_fs(tabs, p, label=b"cheat%d" % s, prover=ch), tabs, p,
                                       label=b"cheat%d" % s)
        self.assertLessEqual(wins / 300, binom_upper(sumcheck.soundness_bound(4, 2, p), 300))

    def test_fiat_shamir_subprotocol_binding(self):
        """A fresh transcript does not bind the tables: all-zero messages fix the challenges r* in advance, and a
        table chosen afterwards with T~(r*) = 0 'proves' a false sum 0. Continuing an outer transcript that
        absorbed a commitment to the table moves r* with the table, and the same forgery fails."""
        from cryptomath.protocols.fiat_shamir import Transcript
        from cryptomath.zk.mle import eq_table
        p, v = P97, 3
        zero = {"claim": 0, "messages": [[0, 0] for _ in range(v)], "v": v, "d": 1}
        t = sumcheck._transcript(v, 1, p, 0, b"toy-sumcheck")
        rstar = []
        for j in range(v):
            for i in range(2):
                t.append(b"s%d_%d" % (j, i), (0).to_bytes(1, "big"))
            rstar.append(t.challenge_scalar(b"r%d" % j, p))
        eq = eq_table(rstar, p)
        table = [0] * 8
        table[0], table[1] = 1, (-eq[0] * pow(eq[1], p - 2, p)) % p      # T~(r*) = 0, but sum T != 0
        self.assertNotEqual(sum(table) % p, 0)
        self.assertTrue(sumcheck.verify_fs(zero, [table], p))             # forged: the false sum 0 is accepted

        def outer():
            tr = Transcript(b"outer")
            tr.append(b"table", bytes(table))                             # stands in for a commitment
            return tr
        self.assertFalse(sumcheck.verify_fs(zero, [table], p, transcript=outer()))
        honest = sumcheck.prove_fs([table], p, transcript=outer())
        self.assertTrue(sumcheck.verify_fs(honest, [table], p, transcript=outer()))


class TestMerkle(unittest.TestCase):
    def test_open_and_pruned_open(self):
        rng = random.Random(6)
        leaves = [bytes([i]) * 3 for i in range(32)]
        T = merkle.MerkleTree(leaves)
        for i in range(32):
            path = T.open(i)
            self.assertEqual(len(path), 5)
            self.assertTrue(merkle.verify(T.root, i, leaves[i], path))
            self.assertFalse(merkle.verify(T.root, i, leaves[i] + b"x", path))
            self.assertFalse(merkle.verify(T.root, i ^ 1, leaves[i], path))
        for _ in range(20):
            I = set(rng.sample(range(32), rng.randrange(1, 9)))
            pf = T.open_many(I)
            opened = {i: leaves[i] for i in I}
            self.assertTrue(merkle.verify_many(T.root, 5, opened, pf))
            self.assertEqual(len(pf) * 32, merkle.proof_size(5, I))
            self.assertLessEqual(merkle.proof_size(5, I), merkle.proof_size(5, I, pruned=False))
            j = next(iter(I))
            self.assertFalse(merkle.verify_many(T.root, 5, {**opened, j: b"tampered"}, pf))
            if pf:
                k = next(iter(pf))
                self.assertFalse(merkle.verify_many(T.root, 5, opened, {**pf, k: b"\x00" * 32}))
                self.assertFalse(merkle.verify_many(T.root, 5, opened, {**pf, (9, 9): b"\x00" * 32}))
        # by hand: depth 3, I = {0, 1}: copath {1, 0, (1,1), (2,1)} minus path -> nodes (1,1), (2,1)
        self.assertEqual(set(merkle.MerkleTree(leaves[:8]).open_many({0, 1})), {(1, 1), (2, 1)})

    def test_binding_and_collision_extraction(self):
        # full SHA-256: changing any leaf changes the root
        leaves = [b"a", b"b", b"c", b"d"]
        roots = {merkle.MerkleTree(leaves).root}
        for i in range(4):
            roots.add(merkle.MerkleTree(leaves[:i] + [b"z"] + leaves[i + 1:]).root)
        self.assertEqual(len(roots), 5)
        # 2-byte digests: a birthday search finds colliding leaves, the trees have equal roots, and
        # two valid openings of different data at one index yield the collision (the binding reduction)
        hb = 2
        x, y = merkle.find_leaf_collision(hb)
        Tx = merkle.MerkleTree([x, b"b", b"c", b"d"], hb)
        Ty = merkle.MerkleTree([y, b"b", b"c", b"d"], hb)
        self.assertEqual(Tx.root, Ty.root)
        self.assertTrue(merkle.verify(Tx.root, 0, x, Tx.open(0), hb) and merkle.verify(Tx.root, 0, y, Ty.open(0), hb))
        a, b = merkle.extract_collision(0, x, Tx.open(0), y, Ty.open(0), hb)
        self.assertNotEqual(a, b)
        self.assertEqual(merkle._h(a, hb), merkle._h(b, hb))
        self.assertIsNone(merkle.extract_collision(0, x, Tx.open(0), x, Tx.open(0), hb))

    def test_hiding_leaves(self):
        leaves = [b"0", b"1", b"0", b"1"]
        T1, T2 = merkle.MerkleTree(leaves, hiding=True), merkle.MerkleTree(leaves, hiding=True)
        self.assertNotEqual(T1.root, T2.root)                  # fresh salts: same data, different roots
        self.assertTrue(merkle.verify(T1.root, 2, b"0", T1.open(2), salt=T1.salts[2]))
        self.assertFalse(merkle.verify(T1.root, 2, b"1", T1.open(2), salt=T1.salts[2]))


class TestFRI(unittest.TestCase):
    P = P97

    def _codeword(self, prm, rng, degree=None):
        f = [rng.randrange(self.P) for _ in range(degree or prm.N)]
        return fri.evaluate_on_domain(f, prm.n0, self.P)

    def test_honest_and_counts(self):
        rng = random.Random(7)
        for prm in (fri.FRIParams(N=8, fold=2, blowup=4, queries=5),
                    fri.FRIParams(N=8, fold=4, blowup=2, queries=4, final_size=2),
                    fri.FRIParams(N=4, fold=2, blowup=8, queries=3, hash_bytes=16)):
            proof = fri.prove(self._codeword(prm, rng), prm, self.P)
            self.assertTrue(fri.verify(proof, prm, self.P), prm)
            self.assertEqual(fri.proof_bytes(proof, self.P), fri.proof_size(prm, self.P)["total"])
        # lower-degree polynomials are also accepted
        prm = fri.FRIParams(N=8, fold=2, blowup=4, queries=5)
        self.assertTrue(fri.verify(fri.prove(self._codeword(prm, rng, degree=3), prm, self.P), prm, self.P))

    def test_hand_count(self):
        # N = 8, k = 2, blowup 4, q = 5, F_97 (1-byte elements), 32-byte hashes:
        # domain 32 -> 16 -> 8 -> 4 -> final constant after r = 3 rounds; leaf counts 16, 8, 4, path depths 4, 3, 2
        prm = fri.FRIParams(N=8, fold=2, blowup=4, queries=5)
        self.assertEqual(fri.num_rounds(prm), 3)
        s = fri.proof_size(prm, self.P)
        self.assertEqual(s["roots"], 3 * 32)
        self.assertEqual(s["final"], 1)
        self.assertEqual(s["leaf_values"], 5 * 3 * 2)
        self.assertEqual(s["paths"], 5 * (4 + 3 + 2) * 32)
        # pruning on the actual query sets can only shrink the paths
        pr = fri.proof_size(prm, self.P, indices={0: {0, 1, 7}, 1: {0, 1, 7}, 2: {0, 1, 3}})
        self.assertLess(pr["paths"], s["paths"])

    def test_tampering_and_high_degree(self):
        rng = random.Random(8)
        prm = fri.FRIParams(N=8, fold=2, blowup=4, queries=6)
        proof = fri.prove(self._codeword(prm, rng), prm, self.P)
        vals, path = proof["queries"][0][1]
        t1 = dict(proof, queries=[[(list(vals[:1]) + [(vals[1] + 1) % self.P], path)
                                   if lvl == 1 else lay for lvl, lay in enumerate(proof["queries"][0])]]
                  + proof["queries"][1:])
        self.assertFalse(fri.verify(t1, prm, self.P))                       # opened value changed
        t2 = dict(proof, final=[(proof["final"][0] + 1) % self.P])
        self.assertFalse(fri.verify(t2, prm, self.P))                       # final polynomial changed
        t3 = dict(proof, roots=[proof["roots"][0][::-1]] + proof["roots"][1:])
        self.assertFalse(fri.verify(t3, prm, self.P))                       # root changed
        # degree 2N - 1 > N: the honest prover's final layer is not constant; rejected in almost every instance
        rejected = sum(not fri.verify(fri.prove(self._codeword(prm, rng, degree=16), prm, self.P), prm, self.P)
                       for _ in range(30))
        self.assertGreaterEqual(rejected, 28)
        # random words (far from the code) are rejected
        for _ in range(10):
            w = [rng.randrange(self.P) for _ in range(prm.n0)]
            self.assertFalse(fri.verify(fri.prove(w, prm, self.P), prm, self.P))

    def test_empirical_soundness_corrupted_cosets(self):
        """Commit layer 0 to a codeword with e corrupted cosets but fold the true codeword: a query catches
        it iff it lands in a corrupted coset, so acceptance = (1 - e / (n_0 / k))^q (up to 1/p coincidences)."""
        rng = random.Random(10)
        trials = 120
        prm = fri.FRIParams(N=8, fold=2, blowup=4, queries=4)
        m0 = prm.n0 // prm.fold
        for e in (2, 4, 8):
            acc = 0
            for t in range(trials):
                good = self._codeword(prm, rng)
                bad = good[:]
                for c in rng.sample(range(m0), e):
                    bad[c] = (bad[c] + 1 + rng.randrange(self.P - 1)) % self.P
                acc += fri.verify(fri.prove(bad, prm, self.P, fold_source=good), prm, self.P)
            expect = (1 - e / m0) ** prm.queries
            self.assertLessEqual(acc / trials, binom_upper(expect + 2 / self.P, trials), (e, acc, expect))


class TestKZG(unittest.TestCase):
    def test_algebra_and_counts(self):
        rng = random.Random(11)
        for N in (1, 4, 16):
            srs = kzg.setup(N, rng=rng)
            p = srs.group.p
            f = [rng.randrange(p) for _ in range(N)]
            with Counter() as c:
                C = kzg.commit(srs, f)
                z = rng.randrange(p)
                y, pi = kzg.open_at(srs, f, z)
                ok = kzg.verify(srs, C, z, y, pi)
            self.assertTrue(ok and y == field.poly_eval(f, z, p))
            self.assertFalse(kzg.verify(srs, C, z, (y + 1) % p, pi))
            # commit N points + open max(1, N - 1) points; group additions as in the MSM formula; 2 pairings
            self.assertEqual(c[MSM_PTS], N + max(1, N - 1))
            self.assertEqual(c[GADD], msm_group_adds(N, p.bit_length()) + msm_group_adds(max(1, N - 1), p.bit_length()))
            self.assertEqual(c[PAIR], 2)
        self.assertEqual(C, field.poly_eval(f, srs.tau_g2, p))           # C is "g^{f(tau)}"

    def test_not_binding(self):
        srs = kzg.setup(4)
        f = [1, 2, 3, 4]
        C = kzg.commit(srs, f)
        pi = kzg.forge_opening(srs, C, 5, 999)
        self.assertTrue(kzg.verify(srs, C, 5, 999, pi))                     # documented: the toy is NOT binding


class TestPlonk(unittest.TestCase):
    def _table(self, rng, p, m=3, n=4):
        cols = [[rng.randrange(p) for _ in range(n)] for _ in range(m)]
        copies = [((0, 1), (1, 0)), ((1, 0), (2, 3)), ((0, 2), (2, 0)), ((1, 3), (2, 2))]
        for a, b in copies:                                      # make the wiring honest
            cols[b[0]][b[1]] = cols[a[0]][a[1]]
        for a, b in copies:
            cols[b[0]][b[1]] = cols[a[0]][a[1]]
        return cols, copies

    def test_permutation_completeness(self):
        rng = random.Random(12)
        for p in (P97, GOLDILOCKS):
            for _ in range(20):
                cols, copies = self._table(rng, p)
                sig = plonk.sigma_from_copies(copies, 3, 4)
                self.assertTrue(all(cols[a[0]][a[1]] == cols[b[0]][b[1]] for a, b in copies))
                beta, gamma = rng.randrange(p), rng.randrange(p)
                Z = plonk.grand_product(cols, sig, beta, gamma, p)
                self.assertTrue(Z is None or Z[-1] == 1)
        # sigma of the identity permutation is the identity labels
        self.assertEqual(plonk.sigma_from_copies([], 2, 3), plonk.identity_labels(2, 3))

    def test_permutation_empirical_soundness(self):
        rng = random.Random(13)
        p, trials = P97, 3000
        cols, copies = self._table(rng, p)
        sig = plonk.sigma_from_copies(copies, 3, 4)
        cols[2][3] = (cols[2][3] + 1) % p                       # break one copy constraint
        acc = sum(plonk.permutation_check(cols, sig, p, rng) for _ in range(trials))
        self.assertLessEqual(acc / trials, binom_upper(plonk.permutation_soundness_bound(3, 4, p), trials))
        self.assertFalse(any(plonk.permutation_check(cols, sig, GOLDILOCKS, rng) for _ in range(50)))

    def test_logup(self):
        rng = random.Random(14)
        p = P97
        table = list(range(16))
        f = [rng.randrange(16) for _ in range(10)]
        mult = plonk.logup_multiplicities(f, table)
        self.assertEqual(sum(mult), len(f))
        good = [plonk.logup_check(f, table, mult, p, rng) for _ in range(200)]
        poles = (len(set(f)) + len(table)) / p
        self.assertGreaterEqual(sum(good) / 200, 1 - binom_upper(poles, 200))   # only pole hits fail
        self.assertTrue(plonk.logup_check(f, table, mult, GOLDILOCKS, rng))
        # out-of-table value with the multiplicities a cheater would use (one in-table entry dropped)
        bad = f[:-1] + [40]
        mult_bad = plonk.logup_multiplicities(f[:-1], table)
        trials = 3000
        acc = sum(plonk.logup_check(bad, table, mult_bad, p, rng) for _ in range(trials))
        self.assertLessEqual(acc / trials, binom_upper(plonk.logup_soundness_bound(len(bad), len(table), p), trials))
        self.assertFalse(any(plonk.logup_check(bad, table, mult_bad, GOLDILOCKS, rng) for _ in range(50)))


class TestConstraintSystems(unittest.TestCase):
    def test_r1cs(self):
        cs = r1cs.R1CS(p=P97, public=["x"], witness=["b0", "b1", "b2"])
        for b in ("b0", "b1", "b2"):
            cs.add({b: 1}, {b: 1, "one": -1}, {}, f"bool[{b}]")
        cs.add({"one": 1}, {"b0": 1, "b1": 2, "b2": 4}, {"x": 1}, "recompose")
        for x in range(8):
            z = {"one": 1, "x": x, **{f"b{i}": (x >> i) & 1 for i in range(3)}}
            self.assertTrue(cs.satisfied(z))
        z = {"one": 1, "x": 5, "b0": 1, "b1": 2, "b2": 0}
        self.assertEqual(cs.failing(z), ["bool[b1]"])     # 1 + 2*2 = 5: recomposition holds
        self.assertEqual(cs.failing({**z, "x": 6}), ["bool[b1]", "recompose"])
        # hand count: 4 constraints; variables one, x, b0..b2; nonzeros 3 * 3 + (1 + 3 + 1)
        self.assertEqual(cs.counts(), {"constraints": 4, "variables": 5, "nonzeros": 14, "max_degree": 2,
                                       "lookups": 0, "table_rows": 0})
        order, A, B, C = cs.matrices()
        self.assertEqual(order[0], "one")
        self.assertEqual(sum(len(r) for M in (A, B, C) for r in M), 14)
        self.assertEqual(B[0][order.index("one")], P97 - 1)

    def test_plonkish(self):
        gates = {"mul": (2, lambda c, _: c["a"] * c["b"] - c["c"]),
                 "acc": (1, lambda c, n: n["a"] - c["c"])}
        t = plonkish.Plonkish(3, gates, table=range(8))
        t.rows += [(("mul", "acc"), {"a": 2, "b": 3, "c": 6}), (("mul",), {"a": 6, "b": 1, "c": 6})]
        t.copies.append(((1, "c"), ("pub", 0)))
        t.lookups.append((0, "b", 1))
        self.assertTrue(t.satisfied([6]))
        self.assertEqual(t.failing([7]), ["copy (1, 'c') = ('pub', 0)"])
        t.rows[0][1]["b"] = 9
        t.rows[0][1]["c"] = 18
        t.rows[1][1]["a"] = 18
        t.rows[1][1]["c"] = 18
        self.assertEqual(t.failing([18]), ["lookup (0, b) x 1"])
        self.assertEqual(t.counts(), {"rows": 2, "height": 8, "height_pow2": 8, "advice_cols": 3, "fixed_cols": 1,
                                      "max_degree": 2, "lookups": 1, "copies": 1, "table_rows": 8})
        self.assertEqual([plonkish.next_pow2(m) for m in (1, 2, 3, 9)], [1, 2, 4, 16])


class TestCostAgreement(unittest.TestCase):
    def test_ntt_butterflies(self):
        q = 97
        for n in (2, 4, 8, 16, 32):
            a = list(range(n))
            with Counter() as c:
                ntt_cyclic(a, q, field.root_of_unity(n, q))
            self.assertEqual(c[BFLY], ntt_butterflies(n))


if __name__ == "__main__":
    unittest.main()
