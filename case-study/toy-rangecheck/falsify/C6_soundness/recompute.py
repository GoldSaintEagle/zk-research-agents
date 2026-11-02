#!/usr/bin/env python3
# TOY: not secure
"""Falsifier: recompute the soundness budget independently, from the parameters the CODE uses
(skills/soundness-budget; agents/falsifier.md step 3).

    python3 falsify/C6_soundness/recompute.py > falsify/C6_soundness/recompute.log

Differences from the theorist's theory/budget.py, on purpose:
  * parameters read off the compiled layout of impl/toy_prover.py (rows, H, lookup groups, number of lookups M,
    table size T, constraint families, zero-check degree, committed columns), not from closed forms;
  * challenges counted as the code squeezes them, and one extra term for the sampling bias of
    Transcript.challenge_scalar (q.bit_length() + 128 bits reduced mod q: statistical distance <= 2^-128 per
    challenge, union over the challenges of the t queries).
Both definitions of [CY24 §Security levels, section:security-levels]; terms from soundness_calc.py.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(PROJ, "impl")]
import toy_prover  # noqa: E402
from range_gadgets import GOLDILOCKS as P, build  # noqa: E402

CALC = os.path.join(PROJ, "..", "..", "skills", "soundness-budget", "scripts", "soundness_calc.py")
KS = (4, 8, 12, 16, 24, 32, 48, 64)


def from_code(arm: str, k: int, n: int = 64, c: int = 8) -> dict:
    t = build(arm, [0] * n, k, c)
    lay = toy_prover.compile_table(t, [0] * n, P)
    v = lay.H.bit_length() - 1
    helpers = toy_prover.logup_helpers(lay, lay.advice, 7) if lay.groups else {}
    _, _, d = toy_prover.zerocheck_tables(lay, lay.advice, helpers, 7, [1] * v, 3)
    M, T = len(t.lookups), len(t.table)
    families = len(lay.gates) + len(lay.pub_cols) + len(lay.groups) + (1 if lay.has_table else 0)
    eps = {"batch+zerocheck": families - 1 + v, "sumcheck": d}
    if lay.groups:
        eps["logup"] = 2 * (M + T) - 1
    rounds = (1 if lay.groups else 0) + 1 + v + (v if lay.has_table else 0)
    challenges = (1 if lay.groups else 0) + v + 1 + v + (v if lay.has_table else 0)
    return {"H": lay.H, "v": v, "M": M, "T": T, "families": families, "d": d, "rounds": rounds,
            "challenges": challenges, "columns": len(lay.advice) + len(helpers), "eps_rbr": max(eps.values())}


def budget(arm, k, pr, level):
    cfg = {"title": f"falsifier recompute {arm} k={k}", "level": level, "lambda": 256, "terms": [
        {"name": "IOP via RBR", "kind": "rbr", "k": pr["rounds"], "eps_rbr": f"{pr['eps_rbr']}/{P}",
         "source": "[CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]"},
        {"name": "Merkle multi-extraction", "kind": "merkle_multi", "ells": [pr["H"]] * pr["columns"],
         "source": "[CY24 §Extractability, lemma:mt-multi-configuration-multi-extractability]"},
        {"name": "challenge sampling bias (per challenge 2^-128)", "kind": "const",
         "eps": f"{pr['challenges']}/{2 ** 128}", "source": "statistical distance of (x mod q), x of bitlen(q)+128 bits"}]}
    path = os.path.join(HERE, "configs", f"{arm}_k{k}_{level}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(cfg, f, indent=1, ensure_ascii=False)
    out = subprocess.run([sys.executable, CALC, "--config", path, "--level", level], capture_output=True, text=True,
                         check=True).stdout
    return float(re.search(r"\*\*Security level: ([\d.]+) bits", out).group(1))


def theorist(arm, k, level):
    t = open(os.path.join(PROJ, "results", "soundness", f"{arm}_k{k}_{level}.txt")).read()
    return float(re.search(r"\*\*Security level: ([\d.]+) bits", t).group(1))


def main() -> int:
    print("| arm | k | rounds | M | T | eps_rbr·p | falsifier worst | theorist worst | falsifier avg | theorist avg | agree |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    worst, avg = [], []
    for arm in ("bits", "lookup"):
        for k in KS:
            pr = from_code(arm, k)
            fw, fa = budget(arm, k, pr, "worst-case"), budget(arm, k, pr, "average-case")
            tw, ta = theorist(arm, k, "worst-case"), theorist(arm, k, "average-case")
            worst.append(fw)
            avg.append(fa)
            print(f"| {arm} | {k} | {pr['rounds']} | {pr['M']} | {pr['T']} | {pr['eps_rbr']} | {fw:g} | {tw:g} | "
                  f"{fa:g} | {ta:g} | {'yes' if (fw, fa) == (tw, ta) else 'NO'} |")
    print(f"\nminimum over the grid: worst-case {min(worst):g} bits, average-case {min(avg):g} bits")
    print("claim C6 needs >= 25 (worst) and >= 50 (average) at every point: "
          f"worst {'holds' if min(worst) >= 25 else 'FAILS'}, average {'holds' if min(avg) >= 50 else 'FAILS'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
