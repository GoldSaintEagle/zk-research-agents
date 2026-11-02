#!/usr/bin/env python3
# TOY: not secure
"""sage-check (skills/sage-check format) of the THEORY.md lemmas, by exhaustion over small prime fields.

    python3 theory/check_gadgets.py > theory/check_gadgets.log

One JSON line per statement; exit 1 if any statement has a counterexample. The statements are about the
*relations* written in circuits/*/SPEC.md (what the constraints should say), not about the code in circuits/:
the code is audited against these relations by the circuit audits (P5 builder, P6 falsifier).

  L1  running-sum bits: {x : exists acc_0..acc_k, acc_0 = 0, d_i(d_i - 1) = 0, acc_k = x} = [0, 2^k), unique, if 2^k < p
  L2  limbs + lookups with the top-limb check: accepted set = [0, 2^k), unique, if 2^k < p and 2^(2c) < p
  L2n without the top-limb check (r = k mod c != 0) the accepted set is [0, 2^(cL)) -- strictly larger
  L3  wrap-around: if 2^k > p, every x < 2^k - p has two decompositions (both encodings)
  L4  logUp identity: if some f_i is not in t, sum 1/(b - f_i) = sum m_j/(b - t_j) holds for at most M + T - 1 values b
"""
from __future__ import annotations

import itertools
import json
import math
import sys


def emit(sid, cases, counterexamples, note=""):
    print(json.dumps({"id": sid, "cases": cases, "counterexamples": counterexamples[:3],
                      "status": "PASS" if not counterexamples else "FAIL", "note": note}))
    return not counterexamples


def bits_solutions(p, k):
    """x -> number of acc vectors; acc_{i+1} = 2 acc_i + d with d in {0, 1} (d(d-1) = 0 has exactly those roots)."""
    sol = {}
    for ds in itertools.product((0, 1), repeat=k):
        acc = 0
        for d in ds:
            acc = (2 * acc + d) % p
        sol[acc] = sol.get(acc, 0) + 1
    return sol


def lookup_solutions(p, k, c, top_check=True):
    L, r = math.ceil(k / c), k % c
    sol = {}
    for limbs in itertools.product(range(2 ** c), repeat=L):          # every limb in the table [0, 2^c)
        if top_check and r and (limbs[0] * 2 ** (c - r)) % p >= 2 ** c:
            continue
        acc = 0
        for l in limbs:
            acc = (2 ** c * acc + l) % p
        sol[acc] = sol.get(acc, 0) + 1
    return sol


def main() -> int:
    ok = True
    # L1
    cex, cases = [], 0
    for p in (11, 13, 17, 97):
        for k in range(1, p.bit_length()):
            if 2 ** k >= p:
                continue
            sol = bits_solutions(p, k)
            for x in range(p):
                cases += 1
                if (x < 2 ** k) != (x in sol) or sol.get(x, 0) > 1:
                    cex.append((p, k, x, sol.get(x, 0)))
    ok &= emit("L1 running-sum bits = [0,2^k), unique (2^k < p)", cases, cex)
    # L2
    cex, cases = [], 0
    for p, k, c in ((17, 3, 2), (17, 4, 2), (67, 5, 3), (67, 6, 3), (257, 7, 4), (257, 5, 4)):
        assert 2 ** k < p and 2 ** (2 * c) < p
        sol = lookup_solutions(p, k, c)
        for x in range(p):
            cases += 1
            if (x < 2 ** k) != (x in sol) or sol.get(x, 0) > 1:
                cex.append((p, k, c, x))
    ok &= emit("L2 limbs + top-limb check = [0,2^k), unique", cases, cex)
    # L2n: the top-limb check is necessary (we *expect* extra accepted values; a counterexample = none found)
    cex, cases = [], 0
    for p, k, c in ((17, 3, 2), (67, 5, 3), (257, 7, 4)):
        cases += 1
        sol = lookup_solutions(p, k, c, top_check=False)
        extra = sorted(x for x in sol if x >= 2 ** k)
        if not extra:
            cex.append((p, k, c))
    ok &= emit("L2n without the top-limb check extra values are accepted (r != 0)", cases, cex,
               note="e.g. p=17,k=3,c=2 accepts " + str(sorted(x for x in lookup_solutions(17, 3, 2, False) if x >= 8)))
    # L3
    cex, cases = [], 0
    for p, k in ((11, 4), (13, 4), (17, 5)):
        sol_b = bits_solutions(p, k)
        sol_l = lookup_solutions(p, k, 2, top_check=True) if 2 ** 4 < p * 4 else {}
        for x in range(2 ** k - p):
            cases += 1
            if sol_b.get(x, 0) < 2:
                cex.append(("bits", p, k, x))
            if k % 2 == 0 and sol_l.get(x, 0) < 2:
                cex.append(("limbs", p, k, x))
    ok &= emit("L3 2^k > p: x < 2^k - p has two witnesses", cases, cex, note="models k = 64 in Goldilocks")
    # L4
    cex, cases = [], 0
    p = 17
    for M, T in ((1, 2), (2, 2), (2, 3)):
        for f in itertools.product(range(5), repeat=M):
            for t in itertools.combinations(range(5), T):
                if all(x in t for x in f):
                    continue
                for m in itertools.product(range(3), repeat=T):
                    cases += 1
                    hits = 0
                    for b in range(p):
                        if b in f or b in t:
                            continue
                        lhs = sum(pow(b - x, p - 2, p) for x in f) % p
                        rhs = sum(mj * pow(b - tj, p - 2, p) for mj, tj in zip(m, t)) % p
                        hits += lhs == rhs
                    if hits > M + T - 1:
                        cex.append((f, t, m, hits))
    ok &= emit("L4 logUp: wrong lookup passes for <= M+T-1 challenges (F_17)", cases, cex)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
