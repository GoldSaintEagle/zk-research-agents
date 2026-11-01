# TOY: not secure -- ALGEBRA DEMO ONLY. The "group" is Z_p with known discrete logarithms; anyone can forge.
"""KZG polynomial commitments, reduced to their algebra.

    ************************************************************************
    *  THIS IS NOT A CRYPTOGRAPHIC IMPLEMENTATION.                          *
    *  A group element g^a is represented by its discrete logarithm a mod p *
    *  and the "pairing" e(g^a, g^b) by a * b mod p. The trapdoor tau is    *
    *  readable from the SRS (srs.tau_g2 = tau), so binding does not hold:      *
    *  :func:`forge_opening` opens any commitment to any value.             *
    ************************************************************************

What it does show is the algebra of KZG
([Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]):

* setup: SRS = (g^{tau^i})_{i < N} for a secret tau;
* commit to f of degree < N: C = g^{f(tau)} = prod_i (g^{tau^i})^{f_i}, one MSM of N points;
* open at z: y = f(z), proof pi = g^{q(tau)} for q(X) = (f(X) - y) / (X - z),
  one MSM of N - 1 points;
* verify: e(C / g^y, g) = e(pi, g^tau / g^z), i.e. f(tau) - y = q(tau)(tau - z).

The MSMs are reported to the active costmodel Counter through
:func:`cryptomath.costmodel.zkops.count_msm`, so the toy's counts line up with
the KZG formulas in :mod:`cryptomath.costmodel.formulas`. Binding in the real
scheme rests on q-type assumptions (q-SDH) in a pairing group whose order is
the field size; nothing of that survives here.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional, Sequence

from ..costmodel.counter import PAIR, count
from ..costmodel.zkops import count_msm
from .field import inv, poly_divmod_linear, poly_eval

__all__ = ["SimulatedGroup", "SRS", "setup", "commit", "open_at", "verify", "forge_opening"]


@dataclass(frozen=True)
class SimulatedGroup:
    """Z_p written multiplicatively: element 'g^a' stored as a. Discrete logs are public."""
    p: int

    def exp(self, base: int, e: int) -> int:        # (g^b)^e
        return base * e % self.p

    def mul(self, a: int, b: int) -> int:           # g^a * g^b
        return (a + b) % self.p

    def div(self, a: int, b: int) -> int:
        return (a - b) % self.p

    def pairing(self, a: int, b: int) -> int:       # e(g^a, g^b) = gT^{ab}
        count(PAIR)
        return a * b % self.p


@dataclass(frozen=True)
class SRS:
    group: SimulatedGroup
    powers: tuple                                    # g^{tau^i}, i < N (stored as tau^i: no secret)
    tau_g2: int                                      # g2^tau of the verifier key (here simply tau)


def setup(N: int, p: int = 2 ** 61 - 1, tau: Optional[int] = None, rng: Optional[random.Random] = None) -> SRS:
    rng = rng or random.Random(0)
    tau = tau if tau is not None else rng.randrange(2, p)
    G = SimulatedGroup(p)
    return SRS(G, tuple(pow(tau, i, p) for i in range(N)), tau)


def _msm(srs: SRS, coeffs: Sequence[int]) -> int:
    count_msm(len(coeffs), srs.group.p.bit_length())
    acc = 0
    for c, g in zip(coeffs, srs.powers):
        acc = srs.group.mul(acc, srs.group.exp(g, c))
    return acc


def commit(srs: SRS, coeffs: Sequence[int]) -> int:
    if len(coeffs) > len(srs.powers):
        raise ValueError("polynomial longer than the SRS")
    return _msm(srs, coeffs)


def open_at(srs: SRS, coeffs: Sequence[int], z: int) -> tuple[int, int]:
    """(y, pi) with y = f(z) and pi = g^{q(tau)}."""
    p = srs.group.p
    q, y = poly_divmod_linear([c % p for c in coeffs], z % p, p)
    return y, _msm(srs, q or [0])


def verify(srs: SRS, C: int, z: int, y: int, pi: int) -> bool:
    G = srs.group
    lhs = G.pairing(G.div(C, G.exp(1, y)), 1)                       # e(C / g^y, g)
    rhs = G.pairing(pi, G.div(srs.tau_g2, G.exp(1, z)))             # e(pi, g^tau / g^z)
    return lhs == rhs


def forge_opening(srs: SRS, C: int, z: int, y_fake: int) -> int:
    """Open C at z to an arbitrary value: possible only because tau is readable from the SRS here."""
    p, tau = srs.group.p, srs.tau_g2
    return (C - y_fake) * inv(tau - z, p) % p


if __name__ == "__main__":
    srs = setup(8)
    f = [3, 1, 4, 1, 5, 9, 2, 6]
    C = commit(srs, f)
    y, pi = open_at(srs, f, 10)
    assert y == poly_eval(f, 10, srs.group.p) and verify(srs, C, 10, y, pi)
    assert not verify(srs, C, 10, y + 1, pi)
    assert verify(srs, C, 10, 12345, forge_opening(srs, C, 10, 12345))   # the toy is not binding
    print("kzg: OK (algebra demo; forgery succeeds as documented)")
