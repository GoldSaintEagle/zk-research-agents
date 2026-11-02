#!/usr/bin/env python3
# TOY: not secure
"""Falsifier: recompute the C4 ratios from the raw per-execution samples in run.json (skills/falsify step 5).

    python3 falsify/C4_time/recompute.py > falsify/C4_time/recompute.log
"""
import os
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "..", "..", "lib", "bench"))
from crbench import stats  # noqa: E402
from crbench.runner import load_run  # noqa: E402

run = load_run(os.path.join(PROJ, "results", "bench_kscan", "run.json"))
fails = [e for e in run.executions if e.returncode != 0]
print(f"bench_kscan: {len(run.executions)} executions, {len(fails)} failed (non-verifying proofs exit 1)")
for k in (4, 8, 12, 16, 24, 32, 48, 64):
    b, l = run.samples(f"bits_k{k}"), run.samples(f"lookup_k{k}")
    sp = stats.speedup(b, l, paired=True)
    print(f"k={k}: n={len(b)}/{len(l)} ratio bits/lookup = {sp.fmt(2)} -> C4 (>= 5x) "
          f"{'holds' if sp.ci_low >= 5 else 'FAILS'}")
