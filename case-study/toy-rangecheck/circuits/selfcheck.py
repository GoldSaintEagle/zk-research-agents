# TOY: not secure
"""Builder self-audit of circuits/range_gadgets.py (owner: circuit-engineer; skills/circuit-audit, procedure step 3).

    python3 circuits/selfcheck.py            # prints one line per check, exit 1 on a failure

Real field (Goldilocks), every k of the experiment grid, both Plonkish arms and R1CS:
  * differential test: 200 random in-range values per k; the generator's witness satisfies the circuit and the
    circuit's public output equals the reference `x < 2^k` (item 10);
  * edge cases 0, 1, 2^k - 1 (item 4);
  * negative tests: out-of-range inputs 2^k, 2^k + 1, p - 1 are rejected (the generator refuses them), and one
    mutated witness cell per constraint family is rejected (item 9).
  * (since v2, after DECISIONS D-5) exhaustive small-field search (items 2-3): the real builders re-run over
    F_11 / F_13 with k = 3, c = 2 (c does not divide k) and every witness cell enumerated.
In v1 the exhaustive search was skipped ("too simple to need it"); the falsifier's exhaustive audit then found the
missing top-limb lookup that the random differential test cannot see.
"""
from __future__ import annotations

import itertools
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from range_gadgets import GOLDILOCKS, VERSION, build, plonk_bits, plonk_lookup, r1cs_bits  # noqa: E402

KS = (4, 8, 12, 16, 24, 32, 48, 63)
P = GOLDILOCKS


def rejects(arm, x, k):
    try:
        t = build(arm, [x], k)
    except ValueError:
        return True                      # the witness generator refuses out-of-range inputs
    return not t.satisfied([x], P)


def exhaustive(make, p: int, k: int) -> bool:
    """Every assignment of the witness cells of a one-value circuit; x = the cell copied to the public input."""
    t = make(0)
    cells = [(r, col) for r, (_, cs) in enumerate(t.rows) for col in sorted(cs)]
    (lr, lc), _ = t.copies[0]
    sols: dict = {}
    for vals in itertools.product(range(p), repeat=len(cells)):
        t.rows = [(gs, dict(cs)) for gs, cs in t.rows]
        for (r, col), v in zip(cells, vals):
            t.rows[r][1][col] = v
        if t.satisfied([t.rows[lr][1][lc]], p):
            x = t.rows[lr][1][lc]
            sols[x] = sols.get(x, 0) + 1
    return set(sols) == set(range(min(p, 2 ** k))) and all(n == 1 for n in sols.values())


def main() -> int:
    rng = random.Random(7)
    fails = 0
    for arm in ("bits", "lookup", "r1cs"):
        for k in KS:
            xs = [rng.randrange(2 ** k) for _ in range(200)] + [0, 1, 2 ** k - 1]
            if arm == "r1cs":
                cs, z = r1cs_bits(xs, k)
                ok_diff = cs.satisfied(z)
                zm = dict(z)
                zm["b0_0"] = (zm["b0_0"] + 2) % P      # booleanity family
                ok_neg = not cs.satisfied(zm)
            else:
                t = build(arm, xs, k)
                ok_diff = t.satisfied(xs, P) and all(x < 2 ** k for x in xs)
                ok_neg = all(rejects(arm, x, k) for x in (2 ** k, 2 ** k + 1, P - 1))
                for fam in t.gates:              # one mutated cell per gate family
                    row = next(i for i, (gs, _) in enumerate(t.rows) if fam in gs)
                    t2 = build(arm, xs, k)
                    cells = dict(t2.rows[row][1])
                    key = "limb" if "limb" in cells and fam == "limb" else "acc"
                    cells[key] = (cells[key] + 3) % P
                    t2.rows[row] = (t2.rows[row][0], cells)
                    ok_neg &= not t2.satisfied(xs, P)
            ok = ok_diff and ok_neg
            fails += not ok
            print(f"selfcheck[{arm} {VERSION}] k={k}: differential 203 inputs {'PASS' if ok_diff else 'FAIL'}; "
                  f"negative tests {'PASS' if ok_neg else 'FAIL'}")
    for p in (11, 13):
        for arm, make in (("bits", lambda x, p=p: plonk_bits([x], 3, p)), ("lookup", lambda x, p=p: plonk_lookup([x], 3, 2, p))):
            ok = exhaustive(make, p, 3)
            fails += not ok
            print(f"selfcheck[{arm} {VERSION}] exhaustive over F_{p}, k = 3, c = 2: {'PASS' if ok else 'FAIL'}")
    print(f"builder self-audit ({VERSION}): {'PASS' if not fails else f'FAIL ({fails})'} "
          "(differential, negative and exhaustive small-field tests)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
