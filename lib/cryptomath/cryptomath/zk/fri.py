# TOY: not secure -- small fields, no coset offset, no proximity-gap parameter choice; demo and counting only.
"""Toy FRI: commit to evaluations of f on a multiplicative subgroup, fold, query, verify.

Parameters (:class:`FRIParams`): folding factor k (power of two), blowup
1/rho (so the evaluation domain has n_0 = N / rho points for degree bound N),
number of queries q, size of the final polynomial sent in the clear, and the
hash length of the Merkle trees.

Folding ([Thaler §10.4.4, Details of FRI: Better Reed-Solomon Proximity Proofs via Interaction]):
write f(X) = sum_{i<k} X^i f_i(X^k); for a verifier challenge alpha the next
function is f'(Y) = sum_i alpha^i f_i(Y) on the domain {x^k}, of size n/k and
degree bound N/k. The k values of f on a coset {x zeta^j} (zeta of order k)
determine f'(x^k) by a size-k inverse DFT, so layer l is committed with one
Merkle leaf per coset (:mod:`cryptomath.zk.merkle`), and a query opens one leaf
per layer and checks it against the folded value of the layer above. After r
rounds the prover sends the final polynomial's coefficients.

Costs ([Thaler §10.4.3, Costs of FRI]): :func:`proof_size` counts the proof
exactly -- r roots, the final coefficients, and per query and layer k field
elements plus a log2(n_l / k)-hash path (or the pruned union of paths for the
actual query set) -- and is checked against the bytes of generated proofs.

Challenges come from a :class:`cryptomath.protocols.fiat_shamir.Transcript`
absorbing every root and the final polynomial. ``prove(..., fold_source=g)``
commits layer 0 to the given evaluations but folds g instead: the cheating
strategy whose acceptance probability is (1 - corrupted cosets / n_0 * k)^q,
measured in tests/test_zk.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from .field import inv, poly_eval, root_of_unity, to_bytes
from .merkle import MerkleTree, verify as merkle_verify

__all__ = ["FRIParams", "fold_coset", "fold_layer", "evaluate_on_domain", "prove", "verify",
           "proof_size", "proof_bytes", "num_rounds"]


@dataclass(frozen=True)
class FRIParams:
    N: int                  # degree bound (number of coefficients), power of two
    fold: int = 2           # folding factor k
    blowup: int = 4         # 1 / rho
    queries: int = 8
    final_size: int = 1     # coefficients of the last polynomial, sent in the clear
    hash_bytes: int = 32

    @property
    def n0(self) -> int:
        return self.N * self.blowup


def num_rounds(prm: FRIParams) -> int:
    r, deg = 0, prm.N
    while deg > prm.final_size:
        deg = -(-deg // prm.fold)
        r += 1
    return r


def _final_coeffs(prm: FRIParams) -> int:
    deg = prm.N
    for _ in range(num_rounds(prm)):
        deg = -(-deg // prm.fold)
    return deg


def evaluate_on_domain(coeffs: Sequence[int], n: int, p: int) -> List[int]:
    w = root_of_unity(n, p)
    return [poly_eval(coeffs, pow(w, t, p), p) for t in range(n)]


def fold_coset(values: Sequence[int], x: int, alpha: int, k: int, p: int) -> int:
    """f'(x^k) from values[j] = f(x zeta^j), zeta a primitive k-th root of unity."""
    zeta_inv = inv(root_of_unity(k, p), p) if k > 1 else 1
    kinv, xinv = inv(k, p), inv(x, p)
    out, a_pow, x_pow = 0, 1, 1
    for i in range(k):
        ci = sum(v * pow(zeta_inv, i * j, p) for j, v in enumerate(values)) % p   # = k x^i f_i(x^k)
        out = (out + a_pow * x_pow * ci) % p
        a_pow, x_pow = a_pow * alpha % p, x_pow * xinv % p
    return out * kinv % p


def fold_layer(evals: Sequence[int], alpha: int, k: int, p: int) -> List[int]:
    n = len(evals)
    m, w = n // k, root_of_unity(n, p)
    return [fold_coset([evals[t + j * m] for j in range(k)], pow(w, t, p), alpha, k, p) for t in range(m)]


def _leaves(evals: Sequence[int], k: int, p: int) -> List[bytes]:
    m = len(evals) // k
    return [b"".join(to_bytes(evals[t + j * m], p) for j in range(k)) for t in range(m)]


def _transcript(prm: FRIParams, p: int):
    from ..protocols.fiat_shamir import Transcript   # lazy: protocols imports sympy via ec
    t = Transcript(b"toy-fri")
    for name, val in (("p", p), ("N", prm.N), ("k", prm.fold), ("blowup", prm.blowup), ("q", prm.queries),
                      ("final", prm.final_size)):
        t.append_int(name.encode(), val)
    return t


def prove(evals: Sequence[int], prm: FRIParams, p: int, fold_source: Optional[Sequence[int]] = None) -> dict:
    """Proof that ``evals`` (on the subgroup of order n_0) is close to degree < N."""
    if len(evals) != prm.n0:
        raise ValueError("evaluations must cover the domain of size N * blowup")
    t = _transcript(prm, p)
    committed, folded = [x % p for x in evals], [x % p for x in (fold_source or evals)]
    trees, layers_c, roots, alphas = [], [], [], []
    for _ in range(num_rounds(prm)):
        tree = MerkleTree(_leaves(committed, prm.fold, p), prm.hash_bytes)
        trees.append(tree)
        layers_c.append(committed)
        roots.append(tree.root)
        t.append(b"root", tree.root)
        alpha = t.challenge_scalar(b"alpha", p)
        alphas.append(alpha)
        folded = fold_layer(folded, alpha, prm.fold, p)
        committed = folded
    n_last = len(committed)
    w = root_of_unity(n_last, p)
    winv, ninv = inv(w, p), inv(n_last, p)
    coeffs = [sum(v * pow(winv, i * s, p) for s, v in enumerate(committed)) * ninv % p for i in range(n_last)]
    final = coeffs[:_final_coeffs(prm)]
    for c in final:
        t.append(b"final", to_bytes(c, p))
    queries = []
    for _ in range(prm.queries):
        s = t.challenge_scalar(b"query", prm.n0)
        q = []
        for lvl, tree in enumerate(trees):
            m = len(layers_c[lvl]) // prm.fold
            c = s % m
            q.append(([layers_c[lvl][c + j * m] for j in range(prm.fold)], tree.open(c)))
            s = c
        queries.append(q)
    return {"roots": roots, "final": final, "queries": queries}


def verify(proof: dict, prm: FRIParams, p: int) -> bool:
    r = num_rounds(prm)
    if len(proof["roots"]) != r or len(proof["final"]) != _final_coeffs(prm) or len(proof["queries"]) != prm.queries:
        return False
    t = _transcript(prm, p)
    alphas = []
    for root in proof["roots"]:
        t.append(b"root", root)
        alphas.append(t.challenge_scalar(b"alpha", p))
    for c in proof["final"]:
        t.append(b"final", to_bytes(c, p))
    for q in proof["queries"]:
        s = t.challenge_scalar(b"query", prm.n0)
        if len(q) != r:
            return False
        n, expected = prm.n0, None
        for lvl in range(r):
            values, path = q[lvl]
            m = n // prm.fold
            c, j = s % m, s // m
            if len(values) != prm.fold:
                return False
            if not merkle_verify(proof["roots"][lvl], c, b"".join(to_bytes(v, p) for v in values), path,
                                 prm.hash_bytes):
                return False
            if expected is not None and values[j] % p != expected:
                return False
            w = root_of_unity(n, p)
            expected = fold_coset(values, pow(w, c, p), alphas[lvl], prm.fold, p)
            s, n = c, m
        if r == 0 or expected != poly_eval(proof["final"], pow(root_of_unity(n, p), s, p), p):
            return False
    return True


def proof_size(prm: FRIParams, p: int, indices: Optional[Dict[int, set]] = None) -> dict:
    """Bytes of a FRI proof. Without ``indices``: unpruned (q separate paths per layer). With
    ``indices`` = {layer: set of opened leaf indices}: each layer's paths pruned to the union."""
    from ..costmodel.zkops import merkle_pruned_nodes
    eb, hb = (p.bit_length() + 7) // 8, prm.hash_bytes
    r, n = num_rounds(prm), prm.n0
    leaves = paths = 0
    for lvl in range(r):
        m = n // prm.fold
        depth = m.bit_length() - 1
        if indices is None:
            leaves += prm.queries * prm.fold * eb
            paths += prm.queries * depth * hb
        else:
            idx = indices[lvl]
            leaves += len(idx) * prm.fold * eb
            paths += merkle_pruned_nodes(depth, idx) * hb
        n = m
    out = {"roots": r * hb, "final": _final_coeffs(prm) * eb, "leaf_values": leaves, "paths": paths}
    out["total"] = sum(out.values())
    return out


def proof_bytes(proof: dict, p: int) -> int:
    """Measured size of a generated (unpruned) proof, field elements at fixed width."""
    eb = (p.bit_length() + 7) // 8
    total = sum(len(r) for r in proof["roots"]) + len(proof["final"]) * eb
    for q in proof["queries"]:
        for values, path in q:
            total += len(values) * eb + sum(len(h) for h in path)
    return total


if __name__ == "__main__":
    import random
    p, rng = 97, random.Random(0)
    prm = FRIParams(N=8, fold=2, blowup=4, queries=6)
    f = [rng.randrange(p) for _ in range(prm.N)]
    pf = prove(evaluate_on_domain(f, prm.n0, p), prm, p)
    assert verify(pf, prm, p) and proof_bytes(pf, p) == proof_size(prm, p)["total"]
    print("fri: OK")
