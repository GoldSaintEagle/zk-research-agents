#!/usr/bin/env python3
# TOY: not secure
"""Soundness budget of the toy argument for every grid point (owner: theorist; skills/soundness-budget).

    python3 theory/budget.py        # writes results/soundness/<arm>_k<k>.json and .txt, prints the summary

Parameters come from the protocol description in THEORY.md and the circuit SPECs (closed forms), not from the
code: n = 64 values, c = 8, Goldilocks p = 2^64 - 2^32 + 1, challenges uniform in F_p, SHA-256 (lambda = 256).

Rounds of the interactive protocol (public coin):
  lookup arm: beta | (tau, alpha) | v zero-check sum-check rounds | v grand-sum sum-check rounds
  bits arm:          (tau, alpha) | v zero-check sum-check rounds
Round-by-round errors (each is a Schwartz-Zippel bound, [Thaler §3.4, Schwartz-Zippel Lemma]):
  beta        logUp rational identity + poles: (2(M + T) - 1)/p        (lib/cryptomath zk.plonk.logup_soundness_bound)
  tau, alpha  batching of m_c constraint families + zero-check in tau: (m_c - 1 + v)/p
  sum-check   d/p per round, d = zero-check degree; 1/p per grand-sum round ([Thaler §4.1, The Sum-Check Protocol])
eps_rbr = max over rounds; Fiat-Shamir via RBR: (t + k_rounds) eps_rbr
([CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]);
Merkle commitments: multi-extraction over the committed columns
([CY24 §Extractability, lemma:mt-multi-configuration-multi-extractability]).
Levels: worst-case and average-case ([CY24 §Security levels, section:security-levels]).
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CALC = os.path.join(PROJ, "..", "..", "skills", "soundness-budget", "scripts", "soundness_calc.py")
P = 2 ** 64 - 2 ** 32 + 1
N, C = 64, 8
KS = (4, 8, 12, 16, 24, 32, 48, 64)


def params(arm: str, k: int) -> dict:
    if arm == "bits":
        rows, T, M = N * (k + 1), 0, 0
        families, d, cols = 3, 4, 1                       # zero, runsum, public copy; acc
    else:
        L, r = math.ceil(k / C), k % C
        rows, T = N * (L + 1), 2 ** C
        M = N * (L + (1 if r else 0))                     # every limb + the shifted top limb (SPEC constraint 4)
        groups = 2 if r else 1
        families, d = 3 + groups + 1, 3                   # zero, limb, public, lookup groups, table
        cols = 3 + groups + 1                             # acc, limb, m, helpers
    H = 1 << max(1, (max(rows, T) - 1).bit_length())
    v = H.bit_length() - 1
    eps = {"zerocheck_batch": families - 1 + v, "sumcheck_round": d}
    if arm == "lookup":
        eps["logup"] = 2 * (M + T) - 1
    rounds = 1 + v + (1 + v if arm == "lookup" else 0)
    return {"arm": arm, "k": k, "rows": rows, "H": H, "v": v, "M": M, "T": T, "families": families, "d": d,
            "columns": cols, "rounds": rounds, "eps_num": eps, "eps_rbr_num": max(eps.values())}


def config(pr: dict, level: str) -> dict:
    return {
        "title": f"toy-rangecheck {pr['arm']} k={pr['k']} (n={N}, c={C}, Goldilocks; TOY)", "level": level,
        "lambda": 256,
        "terms": [
            {"name": f"IOP via RBR, (t + {pr['rounds']}) eps_rbr, eps_rbr = {pr['eps_rbr_num']}/p", "kind": "rbr",
             "k": pr["rounds"], "eps_rbr": f"{pr['eps_rbr_num']}/{P}", "regime": "proven",
             "source": "[CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]; "
                       "rounds: [Thaler §3.4, Schwartz-Zippel Lemma], [Thaler §4.1, The Sum-Check Protocol]; "
                       "logUp: source: other, ePrint 2022/1530"},
            {"name": f"Merkle multi-extraction ({pr['columns']} columns of {pr['H']} leaves)", "kind": "merkle_multi",
             "ells": [pr["H"]] * pr["columns"], "regime": "proven",
             "source": "[CY24 §Extractability, lemma:mt-multi-configuration-multi-extractability]"},
        ]}


def run(cfg_path: str, level: str) -> tuple[str, float]:
    out = subprocess.run([sys.executable, CALC, "--config", cfg_path, "--level", level, "--evidence",
                          "--log", cfg_path[:-5] + ".txt"],
                         capture_output=True, text=True, check=True).stdout
    m = re.search(r"\*\*Security level: ([\d.]+) bits", out)
    return out, float(m.group(1))


def main() -> int:
    outdir = os.path.join(PROJ, "results", "soundness")
    os.makedirs(outdir, exist_ok=True)
    print("| arm | k | H | rounds | eps_rbr·p | worst-case bits | average-case bits |")
    print("|---|---|---|---|---|---|---|")
    for arm in ("bits", "lookup"):
        for k in KS:
            pr = params(arm, k)
            res = {}
            for level in ("worst-case", "average-case"):
                cp = os.path.join(outdir, f"{arm}_k{k}_{level}.json")
                with open(cp, "w") as f:
                    json.dump(config(pr, level), f, indent=1, ensure_ascii=False)
                out, bits = run(os.path.relpath(cp, PROJ), level)
                with open(cp[:-5] + ".txt", "w") as f:
                    f.write(out.replace(os.path.expanduser("~"), "~"))
                res[level] = bits
            print(f"| {arm} | {k} | {pr['H']} | {pr['rounds']} | {pr['eps_rbr_num']} | {res['worst-case']:g} | "
                  f"{res['average-case']:g} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
