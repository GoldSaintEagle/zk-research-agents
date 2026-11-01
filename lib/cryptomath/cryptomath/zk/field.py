# TOY: not secure -- small fields; plain Python ints mod p, nothing constant-time.
"""Small prime fields for the toy proof systems.

Field elements are Python ints in [0, p). Default moduli:

* ``P17 = 17``: 16 = 2^4, roots of unity up to order 16 (hand-checkable);
* ``P97 = 97``: 96 = 2^5 * 3, roots of unity up to order 32;
* ``GOLDILOCKS = 2^64 - 2^32 + 1``: 2-adicity 32, multiplicative generator 7.

Soundness errors of the toy protocols scale like (degree) / p, so F_17 and
F_97 make cheating provers succeed often enough to *measure* the error
(see tests/test_zk.py); Goldilocks shows the same code at a realistic size.

Lagrange interpolation over the points 0..d is what a sum-check verifier uses
to evaluate a round polynomial sent as d + 1 values
([Thaler §2.4, Univariate Lagrange Interpolation]).
"""
from __future__ import annotations

from typing import List, Sequence

__all__ = ["P17", "P97", "GOLDILOCKS", "inv", "batch_inv", "generator", "root_of_unity",
           "poly_eval", "poly_add", "poly_mul", "poly_divmod_linear", "interpolate_eval",
           "interpolate", "to_bytes"]

P17 = 17
P97 = 97
GOLDILOCKS = 2 ** 64 - 2 ** 32 + 1
_KNOWN_GENERATORS = {P17: 3, P97: 5, GOLDILOCKS: 7}


def inv(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError("0 has no inverse")
    return pow(a, p - 2, p)


def batch_inv(xs: Sequence[int], p: int) -> List[int]:
    """Montgomery's trick: n inverses for one inversion and 3(n - 1) multiplications."""
    pref, acc = [], 1
    for x in xs:
        pref.append(acc)
        acc = acc * x % p
    acc = inv(acc, p)
    out = [0] * len(xs)
    for i in range(len(xs) - 1, -1, -1):
        out[i] = acc * pref[i] % p
        acc = acc * xs[i] % p
    return out


def _prime_factors(n: int) -> List[int]:
    out, f = [], 2
    while f * f <= n:
        if n % f == 0:
            out.append(f)
            while n % f == 0:
                n //= f
        f += 1
    if n > 1:
        out.append(n)
    return out


def generator(p: int) -> int:
    """A generator of F_p^* (table for the default moduli, search for small p)."""
    if p in _KNOWN_GENERATORS:
        return _KNOWN_GENERATORS[p]
    fs = _prime_factors(p - 1)
    for g in range(2, p):
        if all(pow(g, (p - 1) // f, p) != 1 for f in fs):
            return g
    raise ValueError(f"no generator found for {p}")


def root_of_unity(n: int, p: int) -> int:
    """A primitive n-th root of unity in F_p (needs n | p - 1)."""
    if (p - 1) % n:
        raise ValueError(f"F_{p} has no element of order {n}")
    return pow(generator(p), (p - 1) // n, p)


def poly_eval(coeffs: Sequence[int], x: int, p: int) -> int:
    """Horner; coeffs[i] is the coefficient of X^i."""
    acc = 0
    for c in reversed(coeffs):
        acc = (acc * x + c) % p
    return acc


def poly_add(a: Sequence[int], b: Sequence[int], p: int) -> List[int]:
    n = max(len(a), len(b))
    return [((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p for i in range(n)]


def poly_mul(a: Sequence[int], b: Sequence[int], p: int) -> List[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % p
    return out


def poly_divmod_linear(coeffs: Sequence[int], z: int, p: int) -> tuple[List[int], int]:
    """Synthetic division by (X - z): returns (quotient, remainder = f(z))."""
    n = len(coeffs)
    if n == 0:
        return [], 0
    q = [0] * (n - 1)
    acc = 0
    for i in range(n - 1, -1, -1):
        acc = (acc * z + coeffs[i]) % p
        if i:
            q[i - 1] = acc
    return q, acc


def interpolate_eval(ys: Sequence[int], r: int, p: int) -> int:
    """Value at r of the unique polynomial of degree < len(ys) through (i, ys[i]), i = 0..d."""
    d1 = len(ys)
    total = 0
    for a, ya in enumerate(ys):
        num = den = 1
        for b in range(d1):
            if b != a:
                num = num * (r - b) % p
                den = den * (a - b) % p
        total = (total + ya * num * inv(den, p)) % p
    return total


def interpolate(xs: Sequence[int], ys: Sequence[int], p: int) -> List[int]:
    """Coefficients of the polynomial of degree < n through the points (xs[i], ys[i])."""
    n = len(xs)
    out = [0] * n
    for i in range(n):
        basis, den = [1], 1
        for j in range(n):
            if j != i:
                basis = poly_mul(basis, [-xs[j] % p, 1], p)
                den = den * (xs[i] - xs[j]) % p
        scale = ys[i] * inv(den, p) % p
        out = poly_add(out, [c * scale % p for c in basis], p)
    return out


def to_bytes(x: int, p: int) -> bytes:
    """Fixed-width big-endian encoding of a field element (for hashing)."""
    return int(x % p).to_bytes((p.bit_length() + 7) // 8, "big")
