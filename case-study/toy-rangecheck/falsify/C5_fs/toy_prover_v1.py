# SNAPSHOT of impl/toy_prover.py as audited at P6 (prover v1, before the fix of DECISIONS D-6). Do not edit.
# TOY: not secure -- no zero knowledge, no polynomial commitment: the verifier reads committed columns in the clear.
"""Toy multilinear Plonkish argument for our range-check circuits (owner: prover-engineer).

One prover for every Plonkish table built by circuits/range_gadgets.py, so both arms of the experiment run the
same code (DECISIONS D-4). Shape: a stripped-down HyperPlonk-style zero-check (source: other, HyperPlonk,
EUROCRYPT 2023) plus logUp for lookups (source: other, ePrint 2022/1530), over the boolean hypercube of
H = 2^v rows:

  1. statement and index absorbed into a Fiat-Shamir transcript (lib/cryptomath protocols.fiat_shamir);
  2. advice columns (and logUp multiplicities) committed with Merkle trees, roots absorbed;
  3. beta squeezed; logUp helper columns h_g = q_g / (beta - s_g col_g) and h_t = q_t m / (beta - t)
     committed;
  4. tau in F^v and alpha squeezed; sum-check of  sum_x eq(tau, x) sum_i alpha^i C_i(x) = 0  over all
     row constraints C_i (gates times selectors, public-input copies, logUp helper constraints)
     ([Thaler §4.1, The Sum-Check Protocol]);
  5. lookup arm only: sum-check of the logUp grand sum  sum_x (sum_g h_g(x) - h_t(x)) = 0.
The verifier replays the transcript, checks every sum-check, and evaluates the final point with the
multilinear extensions of the committed columns, which it reads directly (TOY stand-in for PCS openings).

Per-phase CPU times are printed as `phase: value ms` lines (skills/prover-cost-model convention) by impl/prove.py.
"""
from __future__ import annotations

import hashlib
import os
import sys
import time
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
for d in (os.path.join(HERE, "..", "..", "..", "lib", "cryptomath"), os.path.join(HERE, "..", "circuits")):
    if d not in sys.path:
        sys.path.insert(0, d)
from cryptomath.protocols.fiat_shamir import Transcript  # noqa: E402
from cryptomath.zk import sumcheck  # noqa: E402
from cryptomath.zk.field import batch_inv, to_bytes  # noqa: E402
from cryptomath.zk.merkle import MerkleTree  # noqa: E402
from cryptomath.zk.mle import eq_table  # noqa: E402
from cryptomath.zk.plonkish import Plonkish, next_pow2  # noqa: E402

DOMAIN = b"toy-rangecheck/prover/v1"


@dataclass
class Layout:
    """The table compiled to columns over H = 2^v rows. `fixed` is the index (known to the verifier)."""
    p: int
    H: int
    advice: dict                      # name -> column (prover)
    fixed: dict                       # selectors, public-copy selectors, lookup selectors, table (verifier)
    gates: dict                       # gate name -> (degree, fn(cur, nxt))
    pub_cols: list                    # advice columns copied to public inputs
    groups: list                      # lookup groups (col, shift)
    has_table: bool
    rows: int


def compile_table(t: Plonkish, public: list[int], p: int) -> Layout:
    rows, T = len(t.rows), len(t.table)
    H = next_pow2(max(rows, T, 2))
    names = sorted({k for _, cells in t.rows for k in cells})
    adv = {a: [0] * H for a in names}
    fixed = {f"q:{g}": [0] * H for g in t.gates}
    for i, (gs, cells) in enumerate(t.rows):
        for a, val in cells.items():
            adv[a][i] = val % p
        for g in gs:
            fixed[f"q:{g}"][i] = 1
    pub_cols = sorted({a[1] for a, b in t.copies})
    for a in pub_cols:
        fixed[f"qpub:{a}"] = [0] * H
        fixed[f"pub:{a}"] = [0] * H
    for (r, a), b in t.copies:
        if b[0] != "pub":
            raise ValueError("toy prover: only copies to public inputs are supported")
        fixed[f"qpub:{a}"][r] = 1
        fixed[f"pub:{a}"][r] = public[b[1]] % p
    groups = sorted({(col, shift) for _, col, shift in t.lookups})
    for g in groups:
        fixed[f"qlk:{g[0]}:{g[1]}"] = [0] * H
    for r, col, shift in t.lookups:
        fixed[f"qlk:{col}:{shift}"][r] = 1
    if T:
        fixed["t"] = [x % p for x in t.table] + [0] * (H - T)
        fixed["qt"] = [1] * T + [0] * (H - T)
        cnt = {}
        for r, col, shift in t.lookups:
            v = adv[col][r] * shift % p
            cnt[v] = cnt.get(v, 0) + 1
        adv["m"] = [cnt.get(x % p, 0) for x in t.table] + [0] * (H - T)
    return Layout(p, H, adv, fixed, dict(t.gates), pub_cols, groups, bool(T), rows)


def index_digest(lay: Layout) -> bytes:
    h = hashlib.sha256()
    for name in sorted(lay.fixed):
        if name.startswith("pub:"):
            continue                     # public inputs are absorbed separately, as the statement
        h.update(name.encode() + b"=" + b"".join(to_bytes(x, lay.p) for x in lay.fixed[name]))
    return h.digest()


def commit(col: list[int], p: int) -> bytes:
    return MerkleTree([to_bytes(x, p) for x in col]).root


def statement_transcript(lay: Layout, meta: dict, public: list[int]) -> Transcript:
    tr = Transcript(DOMAIN)
    for key in ("arm", "n", "k", "c"):
        tr.append(key.encode(), str(meta[key]).encode())
    tr.append_int(b"p", lay.p)
    tr.append_int(b"H", lay.H)
    tr.append(b"index", index_digest(lay))
    for j, x in enumerate(public):
        tr.append(b"x%d" % j, to_bytes(x, lay.p))
    return tr


def shifted(col: list[int]) -> list[int]:
    return col[1:] + [0]


def zerocheck_tables(lay: Layout, adv: dict, helpers: dict, beta: int, tau: list[int], alpha: int):
    """Tables of the zero-check and the combine function sum_i alpha^i C_i, times eq(tau, .)."""
    p = lay.p
    names = ["eq"] + sorted(lay.fixed) + sorted(adv) + [f"nxt:{a}" for a in sorted(adv)] + sorted(helpers)
    cols = {"eq": eq_table(tau, p), **lay.fixed, **adv, **{f"nxt:{a}": shifted(adv[a]) for a in adv}, **helpers}
    ix = {nm: i for i, nm in enumerate(names)}
    gates = [(ix[f"q:{g}"], fn) for g, (_, fn) in sorted(lay.gates.items())]
    adv_names = sorted(adv)
    pubs = [(ix[f"qpub:{a}"], ix[a], ix[f"pub:{a}"]) for a in lay.pub_cols]
    looks = [(ix[f"qlk:{c}:{s}"], ix[f"h:{c}:{s}"], ix[c], s) for c, s in lay.groups]
    tab = (ix["qt"], ix["h:t"], ix["t"], ix["m"]) if lay.has_table else None
    e = ix["eq"]

    def combine(v):
        cur = {a: v[ix[a]] for a in adv_names}
        nxt = {a: v[ix["nxt:" + a]] for a in adv_names}
        s, w = 0, 1
        for q, fn in gates:
            s += w * v[q] * fn(cur, nxt)
            w = w * alpha % p
        for q, a, pb in pubs:
            s += w * v[q] * (v[a] - v[pb])
            w = w * alpha % p
        for q, h, c, sh in looks:
            s += w * (v[h] * (beta - sh * v[c]) - v[q])
            w = w * alpha % p
        if tab:
            q, h, t, m = tab
            s += w * (v[h] * (beta - v[t]) - v[q] * v[m])
        return v[e] * s % p

    degree = max(3, max(d for d, _ in lay.gates.values()) + 2)
    return [cols[nm] for nm in names], combine, degree


def grandsum(lay: Layout, helpers: dict):
    hs = [helpers[f"h:{c}:{s}"] for c, s in lay.groups] + [helpers["h:t"]]
    k = len(hs) - 1
    return hs, (lambda v: (sum(v[:k]) - v[k]) % lay.p)


def logup_helpers(lay: Layout, adv: dict, beta: int) -> dict:
    p, H = lay.p, lay.H
    out = {}
    for c, s in lay.groups:
        q = lay.fixed[f"qlk:{c}:{s}"]
        den = [(beta - s * x) % p or 1 for x in adv[c]]          # a zero denominator is a bad challenge (prob. <= H/p)
        inv = batch_inv(den, p)
        out[f"h:{c}:{s}"] = [qi * ii % p for qi, ii in zip(q, inv)]
    if lay.has_table:
        den = [(beta - x) % p or 1 for x in lay.fixed["t"]]
        inv = batch_inv(den, p)
        out["h:t"] = [q * m % p * ii % p for q, m, ii in zip(lay.fixed["qt"], adv["m"], inv)]
    return out


@dataclass
class Proof:
    roots: dict
    helper_roots: dict
    zerocheck: dict
    grandsum: dict | None
    oracle: dict = field(default_factory=dict)      # TOY: the committed columns, read by the verifier in the clear


def prove(t: Plonkish, public: list[int], meta: dict, p: int, timer: dict | None = None) -> Proof:
    timer = {} if timer is None else timer
    clock = time.process_time

    t0 = clock()
    lay = compile_table(t, public, p)
    tr = statement_transcript(lay, meta, public)
    timer["witness"] = clock() - t0

    t0 = clock()
    roots = {a: commit(col, p) for a, col in sorted(lay.advice.items())}
    for a, r in roots.items():
        tr.append(b"root:" + a.encode(), r)
    timer["commit"] = clock() - t0

    t0 = clock()
    helpers, helper_roots = {}, {}
    if lay.groups:
        beta = tr.challenge_scalar(b"beta", p)
        helpers = logup_helpers(lay, lay.advice, beta)
        helper_roots = {h: commit(col, p) for h, col in sorted(helpers.items())}
        for h, r in helper_roots.items():
            tr.append(b"root:" + h.encode(), r)
    else:
        beta = 0
    timer["logup"] = clock() - t0

    t0 = clock()
    v = lay.H.bit_length() - 1
    tau = [tr.challenge_scalar(b"tau%d" % i, p) for i in range(v)]
    alpha = tr.challenge_scalar(b"alpha", p)
    tables, comb, deg = zerocheck_tables(lay, lay.advice, helpers, beta, tau, alpha)
    zc = sumcheck.prove_fs(tables, p, label=b"zerocheck", combine=comb, degree=deg)
    timer["zerocheck"] = clock() - t0

    t0 = clock()
    gs = None
    if lay.has_table:
        hs, gcomb = grandsum(lay, helpers)
        gs = sumcheck.prove_fs(hs, p, label=b"grandsum", combine=gcomb, degree=1)
    timer["grandsum"] = clock() - t0
    return Proof(roots, helper_roots, zc, gs, oracle={**lay.advice, **helpers})


def verify(t_index: Plonkish, public: list[int], meta: dict, proof: Proof, p: int) -> bool:
    """t_index: the circuit built by the verifier from the public parameters (only its fixed part is used)."""
    lay = compile_table(t_index, public, p)
    adv = {a: proof.oracle[a] for a in lay.advice}
    tr = statement_transcript(lay, meta, public)
    for a in sorted(lay.advice):
        if commit(adv[a], p) != proof.roots.get(a):
            return False
        tr.append(b"root:" + a.encode(), proof.roots[a])
    helpers = {}
    if lay.groups:
        beta = tr.challenge_scalar(b"beta", p)
        for h in sorted(proof.helper_roots):
            helpers[h] = proof.oracle[h]
            if commit(helpers[h], p) != proof.helper_roots[h]:
                return False
            tr.append(b"root:" + h.encode(), proof.helper_roots[h])
    else:
        beta = 0
    v = lay.H.bit_length() - 1
    tau = [tr.challenge_scalar(b"tau%d" % i, p) for i in range(v)]
    alpha = tr.challenge_scalar(b"alpha", p)
    tables, comb, _ = zerocheck_tables(lay, adv, helpers, beta, tau, alpha)
    if proof.zerocheck["claim"] != 0 or not sumcheck.verify_fs(proof.zerocheck, tables, p, label=b"zerocheck",
                                                                 combine=comb):
        return False
    if lay.has_table:
        hs, gcomb = grandsum(lay, helpers)
        if proof.grandsum is None or proof.grandsum["claim"] != 0:
            return False
        if not sumcheck.verify_fs(proof.grandsum, hs, p, label=b"grandsum", combine=gcomb):
            return False
    return True


if __name__ == "__main__":
    import random
    from range_gadgets import GOLDILOCKS, build
    rng = random.Random(1)
    for arm in ("bits", "lookup"):
        for k in (4, 12):
            xs = [rng.randrange(2 ** k) for _ in range(4)]
            meta = {"arm": arm, "n": 4, "k": k, "c": 8}
            pr = prove(build(arm, xs, k), xs, meta, GOLDILOCKS)
            assert verify(build(arm, [0] * 4, k), xs, meta, pr, GOLDILOCKS), (arm, k)
            bad = xs[:]
            bad[0] = (bad[0] + 1) % GOLDILOCKS
            assert not verify(build(arm, [0] * 4, k), bad, meta, pr, GOLDILOCKS), (arm, k)
    print("toy_prover: OK")
