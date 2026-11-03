#!/usr/bin/env python3
"""P04 -- parameter-plane feasibility screen (soundness budget vs. proof size).

Pattern: x = FRI blow-up log2(1/rho), y = number of queries t.  Lower
constraint: soundness (t must reach the lambda-bit curve in the PROVEN regime;
the conjectured-regime curve is drawn dashed and labelled, never used to pick
the point); upper constraint: proof-size budget; right constraint: prover
budget (blow-up).  The feasible set is a light tint between them; the chosen
parameter set is a single marked point with a label.  Curves are labelled
in-line.  TOY FORMULAS (per-query error (1+rho)/2 in the unique-decoding
regime, rho in the conjectured one; proof size = t x layers x Merkle path) --
replace by `skills/soundness-budget/scripts/soundness_calc.py` output and the
prover's measured proof sizes (with EVIDENCE rows) before publishing.
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "style"))
import palette as P
import numpy as np

LAMBDA = 128          # target soundness bits
LOG_N = 20            # toy: 2^20-row trace
LAYERS = 10           # toy: FRI layers opened per query
BUDGET_KIB = 1500     # toy proof-size budget
MAX_BLOWUP = 3        # toy prover budget: blow-up <= 8


def toy_queries_proven(b, lam=LAMBDA):
    # TOY: unique-decoding regime, per-query error (1 + rho) / 2
    rho = 2.0 ** -b
    return lam / -np.log2((1 + rho) / 2)


def toy_queries_conjectured(b, lam=LAMBDA):
    # TOY: conjectured regime, per-query error rho (not a proven bound)
    return lam / b


def toy_max_queries(b, budget_kib=BUDGET_KIB):
    # TOY: each query opens LAYERS Merkle paths of (LOG_N + b) 32-byte hashes
    return budget_kib * 1024 / (LAYERS * (LOG_N + b) * 32)


def make(venue="lncs", outdir=ROOT / "examples"):
    b = np.linspace(1, 4, 200)
    lo, hi = toy_queries_proven(b), toy_max_queries(b)
    fig, ax = P.figure(venue, width="full", aspect=0.45)
    ok = (hi >= lo) & (b <= MAX_BLOWUP)
    ax.fill_between(b, lo, hi, where=ok, color=P.FEASIBLE, lw=0, label="feasible")
    ax.plot(b, lo, color=P.OURS_DARK, lw=0.9)
    ax.text(1.05, toy_queries_proven(1.05) + 4, rf" proven, $\lambda={LAMBDA}$", color=P.INK_2, fontsize="small",
            va="bottom", ha="left")
    ax.plot(b, toy_queries_conjectured(b), color=P.INK_2, lw=0.9, linestyle=(0, (4, 2)))
    ax.text(3.3, toy_queries_conjectured(3.3) + 4, rf"conjectured, $\lambda={LAMBDA}$", color=P.INK_2,
            fontsize="small", va="bottom", ha="left")
    ax.plot(b, hi, color=P.CATEGORICAL[7], lw=0.9)
    ax.text(1.05, toy_max_queries(1.05) + 4, f" proof size $\\leq$ {BUDGET_KIB} KiB", color=P.INK,
            fontsize="small", va="bottom", ha="left")
    ax.axvline(MAX_BLOWUP, color=P.INK_2, lw=0.7, linestyle=(0, (1, 1.5)))
    ax.text(MAX_BLOWUP + 0.03, 300, "prover budget", color=P.INK_2, fontsize="small", va="center", ha="left")
    chosen = (3, 160)
    ax.plot([chosen[0]], [chosen[1]], marker="*", ms=9, color=P.ACCENT, mec="white", mew=0.6, zorder=5)
    ax.annotate("chosen set", chosen, xytext=(-8, 3), textcoords="offset points", ha="right", va="bottom",
                fontsize="small")
    ax.text(2.2, 100, "unsound (proven regime)", color=P.INK_MUTED, fontsize="small", style="italic")
    ax.text(2.2, 290, "proof too large", color=P.INK_MUTED, fontsize="small", style="italic")
    ax.set_xticks([1, 2, 3, 4], [r"$1/2$", r"$1/4$", r"$1/8$", r"$1/16$"])
    ax.set_xlabel(r"code rate $\rho$")
    ax.set_ylabel(r"FRI queries $t$")
    ax.set_xlim(1, 4)
    ax.set_ylim(0, 340)
    return P.save(fig, "p04_param_feasibility", outdir)


if __name__ == "__main__":
    P.cli(make, __doc__)
