#!/usr/bin/env python3
# TOY: not secure
"""Falsifier: attack the prover-time claim at the edges of what it quantifies over (skills/falsify, step 4 / 6).

    python3 falsify/C4_time/edges.py > falsify/C4_time/edges.log     # ~1 min, crbench session -> results/falsify_C4_edges/

The thesis fixes c = 8 and n = 64; the falsifier checks whether the conclusion depends on those choices:
limb width c in {4, 8, 16} at k = 32 (table 2^c vs number of limbs), and a smaller statement n = 16.
Same protocol as bench_kscan (interleaved, 1 warm-up + 5 rounds, CPU time, every proof verified).
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "..", "..", "lib", "bench"))
sys.path.insert(0, os.path.join(PROJ, "code"))
from crbench import stats  # noqa: E402
from crbench.runner import run_interleaved  # noqa: E402
from run_experiments import fresh_dir, sanitise  # noqa: E402

PY = sys.executable


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results", help="results directory relative to the project")
    a = ap.parse_args(argv)
    arms = {"bits_n64_k32": f"{PY} impl/prove.py --arm bits --k 32 --n 64",
            "lookup_c4_n64_k32": f"{PY} impl/prove.py --arm lookup --k 32 --n 64 --c 4",
            "lookup_c8_n64_k32": f"{PY} impl/prove.py --arm lookup --k 32 --n 64 --c 8",
            "lookup_c16_n64_k32": f"{PY} impl/prove.py --arm lookup --k 32 --n 64 --c 16",
            "bits_n16_k16": f"{PY} impl/prove.py --arm bits --k 16 --n 16",
            "lookup_c8_n16_k16": f"{PY} impl/prove.py --arm lookup --k 16 --n 16 --c 8"}
    d = os.path.join(PROJ, a.out, "falsify_C4_edges")
    fresh_dir(d)
    r = run_interleaved(arms, repeats=5, warmup=1, order="alternate", parser="generic", metric="time", label="prove",
                        log_dir=os.path.relpath(d, PROJ), threads=1, cwd=PROJ, target_dir=PROJ)
    s = r.summary()
    out = [f"# falsify_C4_edges: rounds={r.repeats} warmup={r.warmup} order={r.order} started={r.started}"]
    for base, cand in (("bits_n64_k32", "lookup_c4_n64_k32"), ("bits_n64_k32", "lookup_c8_n64_k32"),
                       ("bits_n64_k32", "lookup_c16_n64_k32"), ("bits_n16_k16", "lookup_c8_n16_k16")):
        sp = stats.speedup(r.samples(base), r.samples(cand), paired=True)
        out.append(f"{cand} vs {base}: ratio {base.split('_')[0]}/{cand.split('_')[0]} = {sp.fmt(2)} "
                   f"(medians {1e3 * s[base]['median']:.2f} ms / {1e3 * s[cand]['median']:.2f} ms, "
                   f"failures {s[base]['failures'] + s[cand]['failures']})")
    with open(os.path.join(d, "summary.log"), "w") as f:
        f.write("\n".join(out) + "\n")
    sanitise(d)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
