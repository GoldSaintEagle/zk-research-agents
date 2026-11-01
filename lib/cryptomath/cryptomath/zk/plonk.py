# TOY: not secure -- the checks are run in the clear on whole columns; no commitments, no zero-knowledge.
"""PLONK-style permutation argument and the logUp lookup argument, as direct checks.

Permutation (copy constraints) -- grand product, PLONK (source: other, ePrint
2019/953). Columns w_0..w_{m-1} of n rows; every cell (i, j) has the label
id(i, j) = i n + j + 1 (real PLONK uses k_i omega^j; any distinct field
elements work) and sigma maps each cell to the next cell of its copy cycle.
With challenges beta, gamma:

    Z_0 = 1,  Z_{j+1} = Z_j * prod_i (w_ij + beta id(i,j) + gamma) / (w_ij + beta sigma(i,j) + gamma)

and the check is Z_n = 1. If the cells of some cycle do not all hold the same
value, the two products differ as polynomials in (beta, gamma) of total degree
m n, so a random (beta, gamma) passes with probability at most about
m n / p (Schwartz--Zippel, [Thaler §3.4, Schwartz-Zippel Lemma]).

Lookup -- **logUp** was chosen (not plookup); source: other, ePrint 2022/1530.
Values f_1..f_M are claimed to lie in a table t_1..t_T; the prover supplies
multiplicities m_j = #{i : f_i = t_j} and the verifier checks, for random beta,

    sum_i 1 / (beta - f_i) = sum_j m_j / (beta - t_j).

If some f_i is not in the table the two sides differ as rational functions;
after clearing denominators the difference has degree < M + T, so a wrong
claim passes with probability at most (M + T - 1) / p (challenges that hit a
pole are rejected and counted as failures for the cheater). In a real logUp
argument the sums are proven with a sum-check or a univariate grand sum.
"""
from __future__ import annotations

import random
from collections import Counter as _Counter
from typing import Dict, List, Optional, Sequence, Tuple

from .field import batch_inv

__all__ = ["identity_labels", "sigma_from_copies", "grand_product", "permutation_check",
           "permutation_soundness_bound", "logup_multiplicities", "logup_check", "logup_soundness_bound"]

Cell = Tuple[int, int]   # (column, row)


def identity_labels(m: int, n: int) -> List[List[int]]:
    return [[i * n + j + 1 for j in range(n)] for i in range(m)]


def sigma_from_copies(copies: Sequence[Tuple[Cell, Cell]], m: int, n: int) -> List[List[int]]:
    """sigma labels from copy constraints: union cells into classes, map each cell to the next in its class."""
    parent = {(i, j): (i, j) for i in range(m) for j in range(n)}

    def find(c):
        while parent[c] != c:
            parent[c] = parent[parent[c]]
            c = parent[c]
        return c

    for a, b in copies:
        parent[find(a)] = find(b)
    classes: Dict[Cell, List[Cell]] = {}
    for c in sorted(parent):
        classes.setdefault(find(c), []).append(c)
    ids = identity_labels(m, n)
    sigma = [row[:] for row in ids]
    for cyc in classes.values():
        for k, (i, j) in enumerate(cyc):
            ni, nj = cyc[(k + 1) % len(cyc)]
            sigma[i][j] = ids[ni][nj]
    return sigma


def grand_product(columns: Sequence[Sequence[int]], sigma: Sequence[Sequence[int]], beta: int, gamma: int,
                  p: int) -> Optional[List[int]]:
    """The accumulator Z_0..Z_n, or None if a denominator vanishes (bad challenge)."""
    m, n = len(columns), len(columns[0])
    ids = identity_labels(m, n)
    dens = []
    for j in range(n):
        d = 1
        for i in range(m):
            d = d * (columns[i][j] + beta * sigma[i][j] + gamma) % p
        if d == 0:
            return None
        dens.append(d)
    dinv = batch_inv(dens, p)
    Z = [1]
    for j in range(n):
        num = 1
        for i in range(m):
            num = num * (columns[i][j] + beta * ids[i][j] + gamma) % p
        Z.append(Z[-1] * num % p * dinv[j] % p)
    return Z


def permutation_check(columns, sigma, p: int, rng: Optional[random.Random] = None,
                      beta: Optional[int] = None, gamma: Optional[int] = None) -> bool:
    rng = rng or random.Random(0)
    beta = rng.randrange(p) if beta is None else beta
    gamma = rng.randrange(p) if gamma is None else gamma
    Z = grand_product(columns, sigma, beta, gamma, p)
    return Z is not None and Z[-1] == 1


def permutation_soundness_bound(m: int, n: int, p: int) -> float:
    return m * n / p


def logup_multiplicities(f: Sequence[int], table: Sequence[int]) -> List[int]:
    c = _Counter(f)
    return [c.get(t, 0) for t in table]


def logup_check(f: Sequence[int], table: Sequence[int], mult: Sequence[int], p: int,
                rng: Optional[random.Random] = None, beta: Optional[int] = None) -> bool:
    rng = rng or random.Random(0)
    beta = rng.randrange(p) if beta is None else beta
    dl = [(beta - x) % p for x in f]
    dr = [(beta - t) % p for t in table]
    if 0 in dl or 0 in dr:
        return False
    lhs = sum(batch_inv(dl, p)) % p
    rhs = sum(m * y for m, y in zip(mult, batch_inv(dr, p))) % p
    return lhs == rhs


def logup_soundness_bound(M: int, T: int, p: int) -> float:
    """Wrong lookups pass w.p. <= (M + T - 1) / p from the identity plus <= (M + T) / p from poles."""
    return (2 * (M + T) - 1) / p


if __name__ == "__main__":
    p = 97
    cols = [[1, 2, 3], [2, 5, 3], [7, 2, 9]]
    copies = [((0, 1), (1, 0)), ((1, 0), (2, 1)), ((0, 2), (1, 2))]
    sig = sigma_from_copies(copies, 3, 3)
    assert permutation_check(cols, sig, p)
    assert logup_check([1, 3, 3], [0, 1, 2, 3], logup_multiplicities([1, 3, 3], [0, 1, 2, 3]), p)
    print("plonk: OK")
