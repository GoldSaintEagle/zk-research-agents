#!/usr/bin/env python3
# TOY: not secure
"""Falsifier: recompute the row / constraint ratios of C3 and C7 from the counts log (not from the summary table).

    python3 falsify/C3_C7_counts/recount.py > falsify/C3_C7_counts/recount.log
"""
import json
import os

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
rows = [json.loads(l) for l in open(os.path.join(PROJ, "results", "counts", "counts.log")) if l.startswith("{")]
print(f"circuits {rows[0]['version']}, n = {rows[0]['n']}, c = {rows[0]['c']}")
for d in rows:
    b, l, r = d["bits"], d["lookup"], d["r1cs"]
    ratio = b["height_pow2"] / l["height_pow2"]
    floor = "table sets the height" if l["table_rows"] >= l["rows"] else "rows set the height"
    print(f"k={d['k']}: C3 padded {b['height_pow2']}/{l['height_pow2']} = {ratio:g} ({'>= 5' if ratio >= 5 else '< 5'}; "
          f"lookup {floor}); C7 naive R1CS constraints / lookup rows = {r['constraints']}/{l['rows']} = "
          f"{r['constraints'] / l['rows']:.2f}")
print("C7 definitions: R1CS constraints (degree 2, no lookups) and Plonkish rows (with lookups, a table and logUp "
      "helper columns) are different units (skills/constraint-cost §1); the like-for-like comparison is C3.")
