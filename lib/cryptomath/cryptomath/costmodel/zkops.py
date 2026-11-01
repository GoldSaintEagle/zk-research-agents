"""Operation counts of ZK prover / verifier primitives, as plain integer code.

Two layers, kept in step by ``tests/test_costmodel.py``:

* closed forms returning integers (``msm_group_adds``, ``ntt_butterflies``,
  ``merkle_hashes``, ``sumcheck_terms``, ``fri_fold_hashes``, ...), the same
  expressions as the sympy formulas in :mod:`cryptomath.costmodel.formulas`;
* ``count_*`` helpers that report those numbers to the active
  :class:`~cryptomath.costmodel.Counter`, so a prover written against them
  gets per-phase op counts.

Formulas
--------
* MSM of N points with b-bit scalars, Pippenger window c (default
  floor(log2 N) - 2): ceil(b / c) * (N + 2^(c+1)) group additions, i.e.
  O(N b / log N) ([Thaler §19.3.2, Relative Efficiency of Different Operations]).
* Radix-2 NTT of size N: (N/2) log2 N butterflies.
* Merkle tree over L leaves (L a power of two, binary): L leaf hashes and
  L - 1 inner nodes; an unpruned opening of q leaves sends q * log2 L nodes, a
  pruned one sends |copath(I) minus path(I)| nodes
  ([CY24 §Path pruning, lemma:path-pruning-is-copaths-minus-paths]).
* Sum-check over v variables for a summand of degree d in each variable: v
  rounds, the honest prover evaluates the summand sum_j (d+1) 2^(v-j) =
  (d+1)(2^v - 1) times and sends d+1 field elements per round
  ([Thaler §4.1, The Sum-Check Protocol]).
* KZG: commitment = one MSM of N points, opening = one MSM of N - 1 points
  (the quotient), verification = 2 pairings
  ([Thaler §15.2, KZG: Univariate Polynomial Commitments from Pairings and a Trusted Setup]).
* FRI with folding factor 2 at rate 1/rho: commit = interpolate (NTT N) and
  extend (NTT rho N), Merkle tree over rho N leaves; the folding layers commit
  rho N / 2, rho N / 4, ..., 2 leaves; a verifier query walks one path per layer
  ([Thaler §10.4.3, Costs of FRI]).

Stdlib only, like :mod:`cryptomath.costmodel.counter`.
"""
from __future__ import annotations

import math
from typing import Iterable

from .counter import BFLY, GADD, HASH, MSM, MSM_PTS, NTT, PAIR, SC_ROUND, SC_TERM, count

__all__ = [
    "log2_exact", "pippenger_window", "msm_group_adds", "ntt_butterflies", "merkle_hashes",
    "merkle_opening_nodes", "merkle_pruned_nodes", "sumcheck_terms", "sumcheck_proof_elems",
    "fri_fold_hashes", "fri_query_hashes",
    "count_msm", "count_ntt", "count_merkle_commit", "count_sumcheck_prover",
    "count_kzg_commit", "count_kzg_open", "count_kzg_verify", "count_fri_commit",
]


def log2_exact(n: int) -> int:
    """log2 of a power of two (ValueError otherwise)."""
    if n < 1 or n & (n - 1):
        raise ValueError(f"{n} is not a power of two")
    return n.bit_length() - 1


# ------------------------------------------------------------- closed forms ---

def pippenger_window(N: int) -> int:
    return max(1, int(math.log2(N)) - 2)


def msm_group_adds(N: int, scalar_bits: int, window: int | None = None) -> int:
    c = window or pippenger_window(N)
    return math.ceil(scalar_bits / c) * (N + 2 ** (c + 1))


def ntt_butterflies(N: int) -> int:
    return (N // 2) * log2_exact(N)


def merkle_hashes(leaves: int) -> int:
    """Leaf hashes + inner nodes of a binary tree over ``leaves`` leaves."""
    return leaves + (leaves - 1)


def merkle_opening_nodes(depth: int, queries: int) -> int:
    """Authentication-path nodes of ``queries`` separate (unpruned) openings."""
    return queries * depth


def merkle_pruned_nodes(depth: int, indices: Iterable[int]) -> int:
    """|copath(I) minus path(I)| summed over the layers: the hash values a pruned
    multi-opening of the 0-based leaf set I must contain."""
    level, total = set(indices), 0
    for _ in range(depth):
        siblings = {i ^ 1 for i in level}
        total += len(siblings - level)
        level = {i >> 1 for i in level}
    return total


def sumcheck_terms(v: int, d: int) -> int:
    return sum((d + 1) * 2 ** (v - j) for j in range(1, v + 1))


def sumcheck_proof_elems(v: int, d: int) -> int:
    """Field elements sent by the prover: d + 1 evaluations of s_j per round."""
    return v * (d + 1)


def fri_fold_hashes(N: int, rho: int) -> int:
    """Merkle hashes of the folding layers (factor 2): trees over rho N / 2, ..., 2 leaves."""
    total, layer = 0, N * rho // 2
    while layer >= 2:
        total += merkle_hashes(layer)
        layer //= 2
    return total


def fri_query_hashes(N: int, rho: int, queries: int) -> int:
    """Verifier hashes: one unpruned path per query in each layer of depth D, D-1, ..., 1,
    D = log2(rho N)."""
    D = log2_exact(N * rho)
    return queries * D * (D + 1) // 2


# ------------------------------------------------------------ count helpers ---

def count_msm(N: int, scalar_bits: int, window: int | None = None) -> None:
    count(MSM)
    count(MSM_PTS, N)
    count(GADD, msm_group_adds(N, scalar_bits, window))


def count_ntt(N: int) -> None:
    count(NTT)
    count(BFLY, ntt_butterflies(N))


def count_merkle_commit(leaves: int) -> None:
    count(HASH, merkle_hashes(leaves))


def count_sumcheck_prover(v: int, d: int, factor: int = 1) -> None:
    """``factor`` sum-checks of the same shape run in parallel (one set of rounds)."""
    count(SC_ROUND, v)
    count(SC_TERM, factor * sumcheck_terms(v, d))


def count_kzg_commit(N: int, scalar_bits: int) -> None:
    count_msm(N, scalar_bits)


def count_kzg_open(N: int, scalar_bits: int) -> None:
    count_msm(max(1, N - 1), scalar_bits)


def count_kzg_verify() -> None:
    count(PAIR, 2)


def count_fri_commit(N: int, rho: int) -> None:
    count_ntt(N)
    count_ntt(N * rho)
    count_merkle_commit(N * rho)
