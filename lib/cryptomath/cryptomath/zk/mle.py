# TOY: not secure -- small fields, plain Python; for reasoning about multilinear protocols.
"""Multilinear extensions over a prime field.

A table ``t`` of length 2^v is the list of values of a function
f: {0,1}^v -> F_p. Its multilinear extension is the unique polynomial of
degree <= 1 in each variable agreeing with f on the hypercube:

    f~(r) = sum_{b in {0,1}^v} f(b) * eq(b, r),
    eq(x, r) = prod_i (x_i r_i + (1 - x_i)(1 - r_i))

([Thaler §3.5, Low Degree and Multilinear Extensions]).

Variable order: x_1 is the *most significant* bit of the table index, so
binding x_1 := r splits the table into its low and high halves,
t'[i] = (1 - r) t[i] + r t[i + 2^(v-1)]. :func:`fold` is that step; repeated
v times it evaluates f~ in O(2^v) field operations, which is also what a
sum-check prover does round by round (:mod:`cryptomath.zk.sumcheck`).
"""
from __future__ import annotations

from typing import List, Sequence

__all__ = ["num_vars", "bits", "eq", "eq_table", "fold", "mle_eval", "mle_eval_lagrange"]


def num_vars(table: Sequence[int]) -> int:
    n = len(table)
    if n < 1 or n & (n - 1):
        raise ValueError("table length must be a power of two")
    return n.bit_length() - 1


def bits(i: int, v: int) -> List[int]:
    """(x_1, ..., x_v) of table index i, x_1 the most significant bit."""
    return [(i >> (v - 1 - j)) & 1 for j in range(v)]


def eq(x: Sequence[int], r: Sequence[int], p: int) -> int:
    acc = 1
    for xi, ri in zip(x, r, strict=True):
        acc = acc * (xi * ri + (1 - xi) * (1 - ri)) % p
    return acc


def eq_table(r: Sequence[int], p: int) -> List[int]:
    """[eq(b, r) for b in {0,1}^v] in table order, built in 2^(v+1) multiplications."""
    t = [1]
    for ri in r:                                  # each new variable becomes the least significant bit
        t = [y for x in t for y in (x * (1 - ri) % p, x * ri % p)]
    return t


def fold(table: Sequence[int], r: int, p: int) -> List[int]:
    """Bind the first variable x_1 := r."""
    h = len(table) // 2
    return [(table[i] + r * (table[i + h] - table[i])) % p for i in range(h)]


def mle_eval(table: Sequence[int], r: Sequence[int], p: int) -> int:
    """f~(r) by v folds."""
    if len(r) != num_vars(table):
        raise ValueError("point has the wrong number of coordinates")
    t = [x % p for x in table]
    for ri in r:
        t = fold(t, ri, p)
    return t[0]


def mle_eval_lagrange(table: Sequence[int], r: Sequence[int], p: int) -> int:
    """f~(r) = sum_b f(b) eq(b, r): the definition, used as a cross-check."""
    return sum(f * e for f, e in zip(table, eq_table(r, p))) % p


if __name__ == "__main__":
    import random
    rng = random.Random(1)
    p = 97
    tab = [rng.randrange(p) for _ in range(8)]
    for i in range(8):                              # agrees with the table on the hypercube
        assert mle_eval(tab, bits(i, 3), p) == tab[i]
    r = [rng.randrange(p) for _ in range(3)]
    assert mle_eval(tab, r, p) == mle_eval_lagrange(tab, r, p)
    print("mle: OK")
