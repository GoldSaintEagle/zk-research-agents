#!/usr/bin/env python3
# TOY: not secure
"""Falsifier's independent circuit audit of the range-check circuits (skills/circuit-audit, procedure step 2-3).

    python3 falsify/C1_lookup_circuit/audit.py > falsify/C1_lookup_circuit/audit.log

Derived from circuits/*/SPEC.md, not from the builder's report. Small-field model: the **real builders**
(circuits/range_gadgets.py, and the frozen v1 snapshot next to this file) are re-run with p = 11 / 13 for one
value; every assignment of every witness cell is enumerated, and the public x is the cell copied to it (the copy
constraint forces x = last acc, so this enumerates all (x, witness) pairs that can satisfy the circuit).
Reported per gadget: accepted out-of-spec x (under-constrained), in-spec x without a witness (over-constrained),
x with more than one witness (non-unique). Then the real field: a concrete Goldilocks witness for each finding.

Also audited (calibration of the harness on a third-party-in-spirit builder): the planning counter of
skills/constraint-cost (its plonk_lookup), which the P2 numbers came from.
"""
from __future__ import annotations

import importlib.util
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(PROJ, "..", ".."))
sys.path[:0] = [os.path.join(REPO, "lib", "cryptomath"), os.path.join(PROJ, "circuits"),
                os.path.join(REPO, "skills", "constraint-cost", "scripts")]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V1 = load(os.path.join(HERE, "range_gadgets_v1.py"), "range_gadgets_v1")
CUR = load(os.path.join(PROJ, "circuits", "range_gadgets.py"), "range_gadgets_cur")
import constraint_count as CC  # noqa: E402


def audit(name, make, p, k, spec_k=None):
    """make(x) -> Plonkish for the single public value x (honest witness for an in-range x)."""
    spec_k = k if spec_k is None else spec_k
    t = make(0)
    cells = [(r, col) for r, (_, cs) in enumerate(t.rows) for col in sorted(cs)]
    (last_row, last_col), _ = t.copies[0]
    sols: dict = {}
    for vals in itertools.product(range(p), repeat=len(cells)):
        rows = [(gs, dict(cs)) for gs, cs in t.rows]
        for (r, col), v in zip(cells, vals):
            rows[r][1][col] = v
        t.rows = rows
        x = rows[last_row][1][last_col]
        if t.satisfied([x], p):
            sols[x] = sols.get(x, 0) + 1
    under = sorted(x for x in sols if x >= 2 ** spec_k)
    over = [x for x in range(min(p, 2 ** spec_k)) if x not in sols]
    nonu = sorted((x, n) for x, n in sols.items() if n > 1)
    bad = (["UNDER-CONSTRAINED (accepts out-of-spec inputs)"] if under else []) + \
          (["NON-UNIQUE WITNESS"] if nonu else []) + (["OVER-CONSTRAINED (rejects honest inputs)"] if over else [])
    ex = ([f"accepts out-of-spec {under[:8]}"] if under else []) + ([f"#witnesses {nonu[:3]}"] if nonu else []) + \
         ([f"rejects in-spec {over[:3]}"] if over else [])
    verdict = "PASS" if not bad else "FAIL: " + "; ".join(bad)
    print(f"circuit-audit[{name}] exhaustive over F_{p}, k = {k}, {p ** len(cells)} assignments: {verdict}"
          + (f" — {'; '.join(ex)}" if ex else "") + " (falsify/C1_lookup_circuit/audit.py)")
    return not bad


def audit_r1cs(p, k):
    """R1CS bit decomposition of one value: enumerate x and every bit variable over F_p."""
    cs, z0 = CUR.r1cs_bits([0], k, p)
    sols: dict = {}
    for vals in itertools.product(range(p), repeat=len(cs.witness) + 1):
        z = {"one": 1, "x0": vals[0], **dict(zip(cs.witness, vals[1:]))}
        if cs.satisfied(z):
            sols[vals[0]] = sols.get(vals[0], 0) + 1
    under = sorted(x for x in sols if x >= 2 ** k)
    over = [x for x in range(min(p, 2 ** k)) if x not in sols]
    nonu = sorted((x, n) for x, n in sols.items() if n > 1)
    ok = not (under or over or nonu)
    print(f"circuit-audit[range_bits R1CS current {CUR.VERSION} (k = {k})] exhaustive over F_{p}, k = {k}, "
          f"{p ** (len(cs.witness) + 1)} assignments: {'PASS' if ok else f'FAIL under={under} over={over} non-unique={nonu[:3]}'}"
          " (falsify/C1_lookup_circuit/audit.py)")
    return ok


def with_p(builder, p, **kw):
    """Run a builder whose honest witness generator needs an in-range x; the audit overwrites the cells."""
    return lambda x: builder([x], p=p, **kw) if "p" in builder.__code__.co_varnames else builder([x], **kw)


def main() -> int:
    G = CUR.GOLDILOCKS
    print("# small-field model (real builders, n = 1)")
    for p in (11, 13):
        audit("range_lookup buggy v1 (k = 3, c = 2)", lambda x, p=p: V1.plonk_lookup([x], 3, 2, p), p, 3)
    for p in (11, 13):
        audit(f"range_lookup current {CUR.VERSION} (k = 3, c = 2)", lambda x, p=p: CUR.plonk_lookup([x], 3, 2, p), p, 3)
    audit(f"range_lookup current {CUR.VERSION} (k = 4, c = 2, divides)", lambda x: CUR.plonk_lookup([x], 4, 2, 17), 17, 4)
    for p in (11, 13):
        audit(f"range_bits current {CUR.VERSION} (k = 3)", lambda x, p=p: CUR.plonk_bits([x], 3, p), p, 3)
    audit(f"range_bits current {CUR.VERSION} over F_11, k = 4 (2^k > p: wrap-around)", lambda x: CUR.plonk_bits([x], 4, 11), 11, 4)
    for p in (11, 13):
        audit_r1cs(p, 3)
    audit("constraint_count.plonk_lookup (skills/constraint-cost planning counter, k = 2, c = 2)",
          lambda x: CC.plonk_lookup([x], 2, 2), 11, 2)

    print("# real field (Goldilocks)")
    # v1: x = 2^12 with limbs [16, 0] (top limb 16 >= 2^4 passes the 8-bit lookup)
    x = 2 ** 12
    t = V1.plonk_lookup([0], 12, 8, G)
    t.rows[0] = (t.rows[0][0], {"acc": 0, "limb": 16})
    t.rows[1] = (t.rows[1][0], {"acc": 16, "limb": 0})
    t.rows[2] = (t.rows[2][0], {"acc": x})
    print(f"real field: v1 accepts x = 2^12 for k = 12 with limbs [16, 0]: {t.satisfied([x], G)}; "
          f"current {CUR.VERSION}: {_cur_accepts_2_12(G)}")
    # k = 64: x = 5 has two witnesses in both encodings (5 and 5 + p are both < 2^64)
    two = []
    for arm in ("bits", "lookup"):
        honest = CUR.build(arm, [5], 63 if arm == "bits" else 64, 8, G) if arm == "bits" else CUR.plonk_lookup([5], 64, 8, G)
        if arm == "bits":
            honest = _bits64(5 + G, G)
        else:
            honest = _lookup64(5 + G, G)
        two.append(f"{arm}: witness of 5 + p satisfies the k = 64 circuit for x = 5: {honest.satisfied([5], G)}")
    print("real field: k = 64 wrap-around — " + "; ".join(two))
    return 0


def _cur_accepts_2_12(G):
    t = CUR.plonk_lookup([0], 12, 8, G)
    t.rows[0] = (t.rows[0][0], {"acc": 0, "limb": 16})
    t.rows[1] = (t.rows[1][0], {"acc": 16, "limb": 0})
    t.rows[2] = (t.rows[2][0], {"acc": 2 ** 12})
    return t.satisfied([2 ** 12], G)


def _bits64(y, G):
    """The 64-bit running sum of the integer y (> p), as a k = 64 bits circuit for x = y mod p."""
    t = CUR.plonk_bits([0], 64, G)
    acc = 0
    for i in range(64):
        t.rows[i] = (t.rows[i][0], {"acc": acc % G})
        acc = 2 * acc + ((y >> (63 - i)) & 1)
    t.rows[64] = (t.rows[64][0], {"acc": acc % G})
    return t


def _lookup64(y, G):
    t = CUR.plonk_lookup([0], 64, 8, G)
    acc = 0
    for i in range(8):
        limb = (y >> (8 * (7 - i))) & 255
        t.rows[i] = (t.rows[i][0], {"acc": acc % G, "limb": limb})
        acc = 256 * acc + limb
    t.rows[8] = (t.rows[8][0], {"acc": acc % G})
    return t


if __name__ == "__main__":
    sys.exit(main())
