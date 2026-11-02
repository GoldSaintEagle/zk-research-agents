# TOY: not secure
"""One timed prove + verify of the toy argument (owner: prover-engineer). The bench binary of the experiments.

    python3 impl/prove.py --arm bits --k 32 --n 64 [--c 8] [--seed 1]

Prints `phase: value ms` lines (CPU time of each prover phase, skills/prover-cost-model convention), then
`prove time: X ms` (process CPU time of the whole prover; the metric of results/bench_*), `prove_wall elapsed`,
`verify time`, `verified: True|False` and one RESULT line with the circuit's counts. Exit code 1 if the proof
does not verify (crbench then records the execution as a failure).
"""
from __future__ import annotations

import argparse
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import toy_prover  # noqa: E402  (puts lib/cryptomath and circuits/ on sys.path)
from range_gadgets import GOLDILOCKS, VERSION, build  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", choices=["bits", "lookup"], required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--c", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    p = GOLDILOCKS
    rng = random.Random(a.seed)
    xs = [rng.randrange(min(2 ** a.k, p)) for _ in range(a.n)]
    meta = {"arm": a.arm, "n": a.n, "k": a.k, "c": a.c}
    timer: dict = {}
    w0, c0 = time.perf_counter(), time.process_time()
    circ = build(a.arm, xs, a.k, a.c)
    timer["build"] = time.process_time() - c0
    proof = toy_prover.prove(circ, xs, meta, p, timer)
    cpu, wall = time.process_time() - c0, time.perf_counter() - w0
    c1 = time.process_time()
    ok = toy_prover.verify(build(a.arm, [0] * a.n, a.k, a.c), xs, meta, proof, p)
    vcpu = time.process_time() - c1
    for ph in ("build", "witness", "commit", "logup", "zerocheck", "grandsum"):
        print(f"{ph}: {1e3 * timer[ph]:.3f} ms")
    print(f"prove time: {1e3 * cpu:.3f} ms")
    print(f"prove_wall elapsed: {1e3 * wall:.3f} ms")
    print(f"verify time: {1e3 * vcpu:.3f} ms")
    print(f"verified: {ok}")
    cnt = circ.counts()
    v = (max(cnt["height"], 2) - 1).bit_length()
    print(f"RESULT arm={a.arm} n={a.n} k={a.k} c={a.c} circuits={VERSION} rows={cnt['rows']} "
          f"table_rows={cnt['table_rows']} lookups={cnt['lookups']} height_pow2={2 ** v} vars={v} "
          f"zerocheck_degree={proof.zerocheck['d']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
