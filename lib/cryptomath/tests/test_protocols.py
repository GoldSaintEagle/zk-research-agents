"""Tests for cryptomath.protocols."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cryptomath.ec import ModPGroup  # noqa: E402
from cryptomath.protocols import (  # noqa: E402
    Pedersen, SchnorrProver, Transcript, hash_commit, hash_verify, schnorr_extract,
    schnorr_nizk_prove, schnorr_nizk_verify, schnorr_simulate, schnorr_verify,
)

class TestCommitFS(unittest.TestCase):
    def test_hash_commit(self):
        C, r = hash_commit(b"bid=5")
        self.assertTrue(hash_verify(C, b"bid=5", r))
        self.assertFalse(hash_verify(C, b"bid=6", r))

    def test_pedersen(self):
        P = Pedersen()
        c1, r1 = P.commit(10)
        c2, r2 = P.commit(32)
        self.assertTrue(P.verify(P.add(c1, c2), 42, r1 + r2))
        self.assertFalse(P.verify(c1, 11, r1))

    def test_transcript(self):
        t1, t2 = Transcript(b"d"), Transcript(b"d")
        t1.append(b"a", b"xy")
        t2.append(b"a", b"x")
        t2.append(b"", b"y")
        self.assertNotEqual(t1.challenge_bytes(b"c"), t2.challenge_bytes(b"c"))
        t3 = Transcript(b"d")
        t3.append(b"a", b"xy")
        self.assertEqual(Transcript(b"d").challenge_scalar(b"c", 101), Transcript(b"d").challenge_scalar(b"c", 101))
        self.assertEqual(len(t3.challenge_bytes(b"c", 80)), 80)

    def test_schnorr(self):
        G = ModPGroup()
        P = SchnorrProver(987654321, G)
        t = P.commit()
        s = P.respond(55)
        self.assertTrue(schnorr_verify(G, P.y, t, 55, s))
        s2 = P.respond(77)
        self.assertEqual(schnorr_extract(G, t, 55, s, 77, s2), 987654321 % G.order)
        ts, cs, ss = schnorr_simulate(G, P.y, 99)
        self.assertTrue(schnorr_verify(G, P.y, ts, cs, ss))
        y, proof = schnorr_nizk_prove(31337, G, b"ctx")
        self.assertTrue(schnorr_nizk_verify(G, y, proof, b"ctx"))
        self.assertFalse(schnorr_nizk_verify(G, y, proof, b"other"))


if __name__ == "__main__":
    unittest.main()
