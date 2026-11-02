# TOY: not secure
"""Counts of our circuits, read off the built objects (owner: circuit-engineer; skills/constraint-cost §6).

    python3 circuits/count.py [--n 64] [--c 8] [--k 4 8 ...]   # Markdown table + one JSON line per circuit

This is the "compiler output" of the toy: the numbers come from the built R1CS / Plonkish objects, not from
formulas. Height = max(rows, table rows); padded height = next power of two.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from range_gadgets import VERSION, counts  # noqa: E402

KS = (4, 8, 12, 16, 24, 32, 48, 64)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--c", type=int, default=8)
    ap.add_argument("--k", type=int, nargs="+", default=list(KS))
    a = ap.parse_args(argv)
    print(f"# circuits {VERSION}: n = {a.n}, c = {a.c}")
    print("| k | r1cs constraints | r1cs nonzeros | bits rows | bits padded | lookup rows | lookups | table | lookup padded | padded ratio |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    lines = []
    for k in a.k:
        r, b, l = counts("r1cs", a.n, k), counts("bits", a.n, k), counts("lookup", a.n, k, a.c)
        print(f"| {k} | {r['constraints']} | {r['nonzeros']} | {b['rows']} | {b['height_pow2']} | {l['rows']} | "
              f"{l['lookups']} | {l['table_rows']} | {l['height_pow2']} | {b['height_pow2'] / l['height_pow2']:g} |")
        lines.append(json.dumps({"version": VERSION, "n": a.n, "c": a.c, "k": k, "r1cs": r, "bits": b, "lookup": l}))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
