# TOY: not secure -- small fields, no zero-knowledge; the verifier reads the oracle tables directly.
"""The sum-check protocol for a product of multilinear polynomials.

Statement: H = sum_{b in {0,1}^v} g(b) with g = combine(f_1~, ..., f_k~), the
f_i~ multilinear extensions of tables (:mod:`cryptomath.zk.mle`). The default
``combine`` is the product, so g has degree d = k in each variable.

Round j: the prover sends s_j(X) = sum over the remaining hypercube of
g(r_1, ..., r_{j-1}, X, b_{j+1}, ..., b_v) as its d + 1 values s_j(0..d); the
verifier checks s_j(0) + s_j(1) against the running claim, picks r_j and sets
the claim to s_j(r_j). After v rounds it checks the claim against one
evaluation of g at (r_1, ..., r_v) -- here by evaluating the tables' MLEs, in a
real argument by a polynomial-commitment opening
([Thaler §4.1, The Sum-Check Protocol]). Soundness error <= v d / p by the
Schwartz--Zippel lemma ([Thaler §3.4, Schwartz-Zippel Lemma]).

* :class:`Prover` -- honest prover; each evaluation of g at a partially bound
  point is counted as one ``sumcheck_term`` (costmodel), so its counts can be
  compared with :func:`cryptomath.costmodel.zkops.sumcheck_terms`.
* :class:`CheatingProver` -- claims a wrong sum and adds to each s_j a
  polynomial with d roots in F_p chosen to keep s_j(0) + s_j(1) consistent; it
  wins exactly when some challenge hits a root, so its success rate is
  1 - (1 - d/p)^v <= v d / p: the bound is measured in tests/test_zk.py.
* :func:`prove_fs` / :func:`verify_fs` -- non-interactive version: challenges
  r_j are squeezed from a :class:`cryptomath.protocols.fiat_shamir.Transcript`
  that absorbs the statement (v, d, claimed sum) and every round message
  ([Thaler §5.2, The Fiat-Shamir Transformation]). By default the transcript is
  fresh and does **not** contain the tables (the oracle): a prover can then fix
  the challenges first and choose the tables afterwards. When the sum-check is
  a sub-protocol, pass ``transcript=`` -- the outer transcript that already
  absorbed the statement and the commitments to the tables -- so that every
  r_j depends on them ([CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness]).
"""
from __future__ import annotations

import math
import random
from typing import Callable, List, Optional, Sequence

from ..costmodel.counter import SC_ROUND, SC_TERM, count
from .field import interpolate_eval, to_bytes
from .mle import fold, mle_eval, num_vars

__all__ = ["Prover", "CheatingProver", "verify", "run", "prove_fs", "verify_fs", "true_sum",
           "soundness_bound"]

Combine = Callable[[Sequence[int]], int]


def _prod(vals: Sequence[int]) -> int:
    return math.prod(vals)


def true_sum(tables: Sequence[Sequence[int]], p: int, combine: Combine = _prod) -> int:
    n = len(tables[0])
    return sum(combine([t[i] for t in tables]) for i in range(n)) % p


def soundness_bound(v: int, d: int, p: int) -> float:
    return v * d / p


class Prover:
    """Honest prover with the tables in memory; ``degree`` defaults to the number of tables."""

    def __init__(self, tables: Sequence[Sequence[int]], p: int, combine: Combine = _prod,
                 degree: Optional[int] = None):
        self.p, self.combine = p, combine
        self.cur = [[x % p for x in t] for t in tables]
        self.v = num_vars(self.cur[0])
        self.d = degree if degree is not None else len(tables)
        self.claim = true_sum(self.cur, p, combine)

    def message(self) -> List[int]:
        """s_j(0), ..., s_j(d) for the current round."""
        p, half = self.p, len(self.cur[0]) // 2
        count(SC_ROUND)
        out = []
        for x in range(self.d + 1):
            s = 0
            for i in range(half):
                count(SC_TERM)
                s += self.combine([(t[i] + x * (t[i + half] - t[i])) % p for t in self.cur])
            out.append(s % p)
        return out

    def receive(self, r: int) -> None:
        self.cur = [fold(t, r, self.p) for t in self.cur]


class CheatingProver(Prover):
    """Claims ``true sum + delta`` (delta != 0) and stays consistent with the verifier's checks."""

    def __init__(self, tables, p, delta: int = 1, combine: Combine = _prod, degree=None,
                 rng: Optional[random.Random] = None):
        super().__init__(tables, p, combine, degree)
        if delta % p == 0:
            raise ValueError("delta must be nonzero")
        self.rng = rng or random.Random(0)
        self.true_claim, self.claim = self.claim, (self.claim + delta) % p
        self.lie = self.claim
        self._err: Optional[List[int]] = None

    def message(self) -> List[int]:
        honest = super().message()
        p = self.p
        gap = (self.lie - (honest[0] + honest[1])) % p
        if gap == 0:                               # a challenge hit a root earlier: now honest
            self._err = None
            return honest
        # e(X) = gap * prod (X - a_i) / k with k = e~(0) + e~(1), d distinct roots a_i outside {0, 1}
        while True:
            roots = set()
            while len(roots) < self.d:
                roots.add(self.rng.randrange(2, p))
            k = (math.prod(-a for a in roots) + math.prod(1 - a for a in roots)) % p
            if k:
                break
        scale = gap * pow(k, p - 2, p) % p
        err = [scale * math.prod(x - a for a in roots) % p for x in range(self.d + 1)]
        self._err = err
        return [(h + e) % p for h, e in zip(honest, err)]

    def receive(self, r: int) -> None:
        sent = None
        if self._err is not None:
            sent = interpolate_eval(self._err, r, self.p)
        super().receive(r)
        honest_next = true_sum(self.cur, self.p, self.combine)
        self.lie = (honest_next + (sent or 0)) % self.p


def verify(claim: int, messages: Sequence[Sequence[int]], challenges: Sequence[int], final_value: int,
           p: int, d: int) -> bool:
    """Replay the verifier's checks; ``final_value`` = g(r_1, ..., r_v) from the oracle."""
    cur = claim % p
    for msg, r in zip(messages, challenges, strict=True):
        if len(msg) != d + 1 or (msg[0] + msg[1]) % p != cur:
            return False
        cur = interpolate_eval(msg, r, p)
    return cur == final_value % p


def _oracle(tables, point, p, combine) -> int:
    return combine([mle_eval(t, point, p) for t in tables]) % p


def run(tables: Sequence[Sequence[int]], p: int, rng: random.Random, prover: Optional[Prover] = None,
        combine: Combine = _prod, degree: Optional[int] = None) -> dict:
    """Interactive run with challenges from ``rng``; returns claim, messages, challenges, verdict."""
    P = prover or Prover(tables, p, combine, degree)
    claim, msgs, chals = P.claim, [], []
    for _ in range(P.v):
        msgs.append(P.message())
        r = rng.randrange(p)
        chals.append(r)
        P.receive(r)
    ok = verify(claim, msgs, chals, _oracle(tables, chals, p, combine), p, P.d)
    return {"claim": claim, "messages": msgs, "challenges": chals, "accepted": ok}


def _transcript(v: int, d: int, p: int, claim: int, label: bytes, outer=None):
    if outer is None:
        from ..protocols.fiat_shamir import Transcript   # lazy: protocols imports sympy via ec
        t = Transcript(label)
    else:
        t = outer
        t.append(b"sumcheck", label)
    t.append_int(b"p", p)
    t.append_int(b"v", v)
    t.append_int(b"d", d)
    t.append(b"claim", to_bytes(claim, p))
    return t


def prove_fs(tables: Sequence[Sequence[int]], p: int, label: bytes = b"toy-sumcheck",
             combine: Combine = _prod, degree: Optional[int] = None, prover: Optional[Prover] = None,
             transcript=None) -> dict:
    """Non-interactive proof {claim, messages}; challenges are recomputed by the verifier.
    ``transcript``: continue this (outer) transcript instead of starting a fresh one; it is advanced in place,
    so the verifier must pass its own copy, advanced to the same point."""
    P = prover or Prover(tables, p, combine, degree)
    t = _transcript(P.v, P.d, p, P.claim, label, transcript)
    msgs = []
    for j in range(P.v):
        m = P.message()
        msgs.append(m)
        for i, y in enumerate(m):
            t.append(b"s%d_%d" % (j, i), to_bytes(y, p))
        P.receive(t.challenge_scalar(b"r%d" % j, p))
    return {"claim": P.claim, "messages": msgs, "v": P.v, "d": P.d}


def verify_fs(proof: dict, tables: Sequence[Sequence[int]], p: int, label: bytes = b"toy-sumcheck",
              combine: Combine = _prod, transcript=None) -> bool:
    v, d = proof["v"], proof["d"]
    if len(proof["messages"]) != v or v != num_vars(tables[0]):
        return False
    t = _transcript(v, d, p, proof["claim"], label, transcript)
    chals = []
    for j, m in enumerate(proof["messages"]):
        for i, y in enumerate(m):
            t.append(b"s%d_%d" % (j, i), to_bytes(y, p))
        chals.append(t.challenge_scalar(b"r%d" % j, p))
    return verify(proof["claim"], proof["messages"], chals, _oracle(tables, chals, p, combine), p, d)


if __name__ == "__main__":
    rng = random.Random(3)
    p = 97
    tabs = [[rng.randrange(p) for _ in range(16)] for _ in range(3)]
    assert run(tabs, p, rng)["accepted"]
    T = 4000
    wins = sum(run(tabs, p, rng, CheatingProver(tabs, p, rng=rng))["accepted"] for _ in range(T))
    exact, bound = 1 - (1 - 3 / p) ** 4, soundness_bound(4, 3, p)
    assert wins / T <= bound + 4 * (bound * (1 - bound) / T) ** 0.5, wins
    print(f"sumcheck: OK (cheater accepted {wins / T:.3f}; exact {exact:.3f}, bound v*d/p = {bound:.3f})")
