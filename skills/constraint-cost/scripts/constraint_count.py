#!/usr/bin/env python3
# TOY: not secure. Toy constraint builders and a toy evaluator; for planning-stage counts only.
"""constraint_count.py -- count constraints, rows and columns of one toy computation written four ways.

    python3 constraint_count.py                          # n = 1024 values, k = 64 bits, limbs c = 8, 16
    python3 constraint_count.py --n 4096 --k 32 --c 8 12 16
    python3 constraint_count.py --poseidon 3 8 57        # R1CS estimate for a HADES/Poseidon permutation
    python3 constraint_count.py --selftest

The computation: range-check n public values to k bits (x_j < 2^k). Four encodings:

  r1cs-bits      R1CS, bit decomposition: per value k booleanity constraints b(b-1) = 0 and one
                 recomposition constraint x = sum 2^i b_i
                 ([Thaler §6.5.4, Details of the Transformation]; R1CS: [Thaler §8.4, Extension from Circuit-SAT to R1CS-SAT]);
  plonk-bits     vanilla Plonkish gate (3 wires, degree 2): one booleanity row and one accumulation row per bit;
  plonk-runsum   one custom degree-2 gate per bit on a running sum acc' = 2 acc + b, (acc' - 2acc)(acc' - 2acc - 1) = 0;
  plonk-lookup   c-bit limbs, running sum acc' = 2^c acc + limb, each limb looked up in a fixed table [0, 2^c);
                 a top limb narrower than c bits costs one extra shifted lookup
                 (lookups for range checks: [Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields]).

Counts are read off the constraint lists the builders actually produce (and the builders are checked on
honest and dishonest witnesses in --selftest), then compared with closed forms. These are planning numbers
(P2): numbers for the paper come from the real compiler's output (see SKILL.md).
Pure Python 3.10+, no third-party dependencies. The R1CS and Plonkish classes (satisfiability, counts) are
lib/cryptomath/cryptomath/zk/{r1cs,plonkish}.py; --poseidon reuses lib/cryptomath/cryptomath/symmetric/afcost.py.
"""
from __future__ import annotations

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "lib", "cryptomath"))
from cryptomath.zk.plonkish import Plonkish, next_pow2  # noqa: E402
from cryptomath.zk.r1cs import P_TOY, R1CS  # noqa: E402   (P_TOY = 2^31 - 1: evaluator field, k <= 30)


# ----------------------------------------------------------------- R1CS ---

def r1cs_bits(n: int, k: int) -> R1CS:
    cs = R1CS()
    for j in range(n):
        x, bits = f"x{j}", [f"b{j}_{i}" for i in range(k)]
        cs.public.append(x)
        for b in bits:
            cs.add({b: 1}, {b: 1, "one": -1}, {})
        cs.add({"one": 1}, {b: 2 ** i for i, b in enumerate(bits)}, {x: 1})
    return cs


def r1cs_bits_witness(xs: list[int], k: int) -> dict:
    z = {"one": 1}
    for j, x in enumerate(xs):
        z[f"x{j}"] = x
        z.update({f"b{j}_{i}": (x >> i) & 1 for i in range(k)})
    return z


# ------------------------------------------------------------- Plonkish ---

def plonk_bits(xs: list[int], k: int) -> Plonkish:
    """Vanilla gate qL a + qR b + qO c + qM ab + qC = 0, written out per row as two named gate shapes:
    bool: a*b - a = 0 with a, b copies of the same bit; acc: a + 2^i b - c = 0."""
    gates = {"bool": (2, lambda c, _: c["a"] * c["b"] - c["a"])}
    t = Plonkish(3, gates)
    for i in range(1, k):
        gates[f"acc{i}"] = (1, (lambda i: lambda c, _: c["a"] + (2 ** i) * c["b"] - c["c"])(i))
    for j, x in enumerate(xs):
        bits = [(x >> i) & 1 for i in range(k)]
        bool_rows = []
        for b in bits:
            bool_rows.append(len(t.rows))
            t.rows.append((("bool",), {"a": b, "b": b, "c": 0}))
            t.copies.append(((bool_rows[-1], "a"), (bool_rows[-1], "b")))
        acc, prev = bits[0], (bool_rows[0], "a")
        for i in range(1, k):
            r = len(t.rows)
            t.rows.append(((f"acc{i}",), {"a": acc, "b": bits[i], "c": acc + (bits[i] << i)}))
            t.copies += [((r, "a"), prev), ((r, "b"), (bool_rows[i], "a"))]
            acc, prev = acc + (bits[i] << i), (r, "c")
        t.copies.append((prev, ("pub", j)))
    return t


def plonk_runsum(xs: list[int], k: int) -> Plonkish:
    """One row per bit plus one, MSB first: acc_0 = 0, acc_{i+1} = 2 acc_i + b; the gate on row i reads acc_i
    and acc_{i+1} (next row) and enforces d (d - 1) = 0 for d = acc_{i+1} - 2 acc_i. The last acc is copied to x."""
    gates = {"runsum": (2, lambda c, n: (n["acc"] - 2 * c["acc"]) * (n["acc"] - 2 * c["acc"] - 1)),
             "zero": (1, lambda c, _: c["acc"])}
    t = Plonkish(1, gates)
    for j, x in enumerate(xs):
        acc = 0
        t.rows.append((("zero", "runsum"), {"acc": 0}))
        for i in reversed(range(k)):
            acc = 2 * acc + ((x >> i) & 1)
            t.rows.append((("runsum",) if i else (), {"acc": acc}))
        t.copies.append(((len(t.rows) - 1, "acc"), ("pub", j)))
    return t


def plonk_lookup(xs: list[int], k: int, c: int) -> Plonkish:
    """MSB-first running sum over limbs: acc_0 = 0, acc_{i+1} = 2^c acc_i + limb_i, limb_i in [0, 2^c) by lookup.
    If r = k mod c != 0 the top limb has only r bits: it is looked up a second time multiplied by 2^(c-r),
    which forces limb < 2^r. Without the `zero` gate acc_0 would be free and every x would pass
    (x = 2^(cL) acc_0 + limbs); the last row holds only acc, so no witness cell is left unconstrained."""
    L, r = math.ceil(k / c), k % c
    gates = {"limb": (1, lambda cur, nxt: nxt["acc"] - (2 ** c) * cur["acc"] - cur["limb"]),
             "zero": (1, lambda cur, _: cur["acc"])}
    t = Plonkish(2, gates, table=range(2 ** c))
    for j, x in enumerate(xs):
        limbs = [(x >> (c * i)) & (2 ** c - 1) for i in reversed(range(L))]   # MSB first
        acc = 0
        for i, limb in enumerate(limbs):
            row = len(t.rows)
            t.rows.append((("limb", "zero") if i == 0 else ("limb",), {"acc": acc, "limb": limb}))
            t.lookups.append((row, "limb", 1))
            if i == 0 and r:
                t.lookups.append((row, "limb", 2 ** (c - r)))
            acc = (2 ** c) * acc + limb
        t.rows.append(((), {"acc": acc}))
        t.copies.append(((len(t.rows) - 1, "acc"), ("pub", j)))
    return t


# --------------------------------------------------------------- counts ---

def count_r1cs(cs: R1CS) -> dict:
    return cs.counts()


def count_plonkish(t: Plonkish) -> dict:
    return t.counts()


def closed_forms(n: int, k: int, c: int) -> dict:
    """The same counts as formulas (what the builders must reproduce)."""
    L, r = math.ceil(k / c), k % c
    return {
        "r1cs-bits": {"constraints": n * (k + 1), "variables": 1 + n * (k + 1), "nonzeros": n * (3 * k + k + 2)},
        "plonk-bits": {"rows": n * (2 * k - 1), "copies": n * (k + 2 * (k - 1) + 1)},
        "plonk-runsum": {"rows": n * (k + 1)},
        "plonk-lookup": {"rows": n * (L + 1), "lookups": n * (L + (1 if r else 0)), "table_rows": 2 ** c},
    }


def estimate(n: int, k: int, c: int) -> dict:
    """Closed-form counts at sizes too large to build (same formulas the self-test checks on small cases)."""
    f = closed_forms(n, k, c)
    L = math.ceil(k / c)
    look_h = max(f["plonk-lookup"]["rows"], 2 ** c)
    return {
        "r1cs-bits": {**f["r1cs-bits"], "max_degree": 2, "lookups": 0, "height_pow2": next_pow2(n * (k + 1))},
        "plonk-bits": {"rows": f["plonk-bits"]["rows"], "advice_cols": 3, "max_degree": 2, "lookups": 0,
                       "height_pow2": next_pow2(f["plonk-bits"]["rows"])},
        "plonk-runsum": {"rows": f["plonk-runsum"]["rows"], "advice_cols": 1, "max_degree": 2, "lookups": 0,
                         "height_pow2": next_pow2(f["plonk-runsum"]["rows"])},
        f"plonk-lookup c={c}": {"rows": f["plonk-lookup"]["rows"], "advice_cols": 2, "fixed_cols": 1,
                                "max_degree": 1, "lookups": f["plonk-lookup"]["lookups"], "table_rows": 2 ** c,
                                "height_pow2": next_pow2(look_h), "limbs": L},
    }


def markdown(rows: dict) -> str:
    cols = ["constraints", "rows", "nonzeros", "advice_cols", "fixed_cols", "max_degree", "lookups",
            "table_rows", "height_pow2"]
    out = ["| encoding | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for name, r in rows.items():
        out.append(f"| {name} | " + " | ".join(str(r.get(col, "")) for col in cols) + " |")
    return "\n".join(out)


def poseidon_r1cs(t: int, R_F: int, R_P: int, alpha: int = 5) -> dict:
    """R1CS estimate for a HADES-type permutation: one constraint per multiplication of the S-boxes
    (afcost.power_mult_cost), linear layers free. Real gadgets differ (e.g. merged constraints, partial-round
    tricks): use the compiler's count in the paper."""
    from cryptomath.symmetric.afcost import hades_cost
    hc = hades_cost(t, R_F, R_P, alpha)
    return {"name": hc.name, "sboxes": hc.nonlinear_ops, "r1cs_constraints": hc.mults,
            "plonkish_rows_deg_alpha_gate": hc.nonlinear_ops}


# ------------------------------------------------------------- selftest ---

def selftest() -> int:
    n, k = 3, 10
    xs = [0, 2 ** k - 1, 613]
    for c in (3, 4, 5):
        f = closed_forms(n, k, c)
        cs = r1cs_bits(n, k)
        z = r1cs_bits_witness(xs, k)
        assert cs.satisfied(z)
        assert {key: count_r1cs(cs)[key] for key in f["r1cs-bits"]} == f["r1cs-bits"], (count_r1cs(cs), f)
        t1, t2, t3 = plonk_bits(xs, k), plonk_runsum(xs, k), plonk_lookup(xs, k, c)
        for t in (t1, t2, t3):
            assert t.satisfied(xs), t
        assert count_plonkish(t1)["rows"] == f["plonk-bits"]["rows"]
        assert count_plonkish(t1)["copies"] == f["plonk-bits"]["copies"]
        assert count_plonkish(t2)["rows"] == f["plonk-runsum"]["rows"]
        c3 = count_plonkish(t3)
        assert (c3["rows"], c3["lookups"], c3["table_rows"]) == (f["plonk-lookup"]["rows"],
                                                                  f["plonk-lookup"]["lookups"], 2 ** c)
        # soundness of each encoding on an out-of-range value: x = 2^k cannot be completed honestly
        bad = [2 ** k]
        assert not plonk_lookup(bad, k, c).satisfied(bad), c
    # a cheating bit (b = 2) breaks booleanity in R1CS and in both bit encodings
    z = r1cs_bits_witness([5], 3)
    z["b0_1"] = 2
    z["b0_0"] = (5 - 2 * 2 - 4) % P_TOY      # keep the recomposition satisfied
    assert not r1cs_bits(1, 3).satisfied(z)
    t = plonk_runsum([5], 3)
    t.rows[2] = (t.rows[2][0], {"acc": 2 * t.rows[1][1]["acc"] + 2})
    assert not t.satisfied([5])
    # the shifted lookup is what range-limits the top limb: without it, x = 2^k passes when c does not divide k
    k2, c2 = 10, 4
    t = plonk_lookup([2 ** k2], k2, c2)
    t.lookups = [lk for lk in t.lookups if lk[2] == 1]
    assert t.satisfied([2 ** k2])
    # acc_0 is constrained: a free first accumulator would let x = 2^(cL) acc_0 + limbs pass for any x
    t = plonk_lookup([5], 8, 4)
    t.rows[0] = (t.rows[0][0], {**t.rows[0][1], "acc": 1})
    acc = 1
    for i in range(2):
        acc = 16 * acc + t.rows[i][1]["limb"]
        t.rows[i + 1] = (t.rows[i + 1][0], {**t.rows[i + 1][1], "acc": acc})
    assert not t.satisfied([acc]), "plonk_lookup accepts a free acc_0"
    # padding and table height: the lookup encoding's height is at least the table size
    e = estimate(4, 8, 16)
    assert e["plonk-lookup c=16"]["height_pow2"] == 2 ** 16 and e["plonk-runsum"]["height_pow2"] == 64
    # crossover in rows (n = 1024, k = 64): 16-bit limbs fill a 2^16 table, 8-bit limbs do not
    e8, e16 = estimate(1024, 64, 8), estimate(1024, 64, 16)
    assert e8["plonk-lookup c=8"]["rows"] == 1024 * 9 and e16["plonk-lookup c=16"]["height_pow2"] == 2 ** 16
    # Poseidon estimate through afcost (x^5 = 3 multiplications per S-box)
    pe = poseidon_r1cs(3, 8, 57)
    assert pe["sboxes"] == 3 * 8 + 57 and pe["r1cs_constraints"] == 3 * pe["sboxes"]
    print("selftest: OK")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=1024, help="number of values to range-check")
    ap.add_argument("--k", type=int, default=64, help="bits per value")
    ap.add_argument("--c", type=int, nargs="+", default=[8, 16], help="limb sizes for the lookup encoding")
    ap.add_argument("--poseidon", type=int, nargs=3, metavar=("T", "RF", "RP"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.poseidon:
        print(poseidon_r1cs(*a.poseidon))
        return 0
    rows = {}
    for c in a.c:
        rows.update(estimate(a.n, a.k, c))
    print(f"range check of n = {a.n} values to k = {a.k} bits (planning estimate; paper numbers come from the compiler)")
    print(markdown(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
