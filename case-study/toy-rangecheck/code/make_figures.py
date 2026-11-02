# TOY: not secure
"""P7 figure from logged data only (owner: figure-artist; skills/paper-figures, pattern P12 of figures/PATTERNS.md).

    python3 code/make_figures.py      # -> paper/figs/fig_ratio_vs_k.{pdf,png}

Inputs: results/bench_kscan/run.json (raw per-execution samples; ratios and paired bootstrap CIs recomputed with
crbench.stats) and results/counts/counts.log (padded heights). No number is typed in here; the 5x target and the
1x break-even line are the thesis' constants. House style: figures/style/palette.py (LNCS width).
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
REPO = os.path.join(PROJ, "..", "..")
sys.path[:0] = [os.path.join(REPO, "figures", "style"), os.path.join(REPO, "lib", "bench")]
import palette as P  # noqa: E402
from crbench import stats  # noqa: E402
from crbench.runner import load_run  # noqa: E402

KS = (4, 8, 12, 16, 24, 32, 48, 64)


def main() -> int:
    run = load_run(os.path.join(PROJ, "results", "bench_kscan", "run.json"))
    sp = [stats.speedup(run.samples(f"bits_k{k}"), run.samples(f"lookup_k{k}"), paired=True) for k in KS]
    cnt = {d["k"]: d for d in (json.loads(l) for l in open(os.path.join(PROJ, "results", "counts", "counts.log"))
                               if l.startswith("{"))}
    rows = [cnt[k]["bits"]["height_pow2"] / cnt[k]["lookup"]["height_pow2"] for k in KS]
    fig, ax = P.figure("lncs", width="full", aspect=0.42)
    x = list(range(len(KS)))
    ax.axhspan(0.5, 1.0, color=P.DANGER, lw=0, alpha=0.6)
    ax.axhline(5, color=P.INK_2, lw=0.8, ls="--")
    ax.text(len(KS) - 1, 5.3, r"thesis v0: 5$\times$", ha="right", va="bottom", fontsize="small", color=P.INK_2)
    ax.axhline(1, color=P.INK_2, lw=0.6)
    ax.text(0, 0.62, "bits wins", ha="left", fontsize="small", color=P.INK_2)
    ax.plot(x, rows, color=P.BASELINE_GREYS[1], marker="s", ms=3.5, lw=1, label="padded rows, bits / lookup")
    ax.errorbar(x, [s.ratio for s in sp], yerr=[[s.ratio - s.ci_low for s in sp], [s.ci_high - s.ratio for s in sp]],
                color=P.OURS, marker="o", ms=3.5, lw=1.2, capsize=2, label="prover CPU time, bits / lookup (95% CI)")
    ax.set_yscale("log", base=2)
    ax.set_ylim(0.5, 12)
    ax.set_yticks([0.5, 1, 2, 4, 8])
    ax.set_yticklabels([f"{t:g}$\\times$" for t in (0.5, 1, 2, 4, 8)])
    ax.set_xticks(x)
    ax.set_xticklabels([str(k) for k in KS])
    ax.set_xlabel("range width $k$ (bits); $n = 64$ values, 8-bit limbs")
    ax.set_ylabel("advantage of logUp")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.22), fontsize="small")
    out = os.path.join(PROJ, "paper", "figs")
    os.makedirs(out, exist_ok=True)
    P.save(fig, "fig_ratio_vs_k", out)
    print("wrote paper/figs/fig_ratio_vs_k.{pdf,png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
