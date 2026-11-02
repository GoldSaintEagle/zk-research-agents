# TOY: not secure
"""Rebuild EVIDENCE.md from the raw logs (owner: experimenter; skills/log-to-evidence).

    python3 code/ledger.py            # rewrites EVIDENCE.md, then runs `crbench evidence check --root .`

Every value is recomputed here from the raw files -- per-execution samples in run.json, the counts log, the
soundness_calc outputs, the falsifier logs -- never copied from a summary. Rows are appended with
crbench.evidence.append_row (the same writer as `crbench evidence add`), so the ledger has the SPEC §3 columns.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "..", "..", "lib", "bench"))
from crbench import stats  # noqa: E402
from crbench.envcapture import capture_env  # noqa: E402
from crbench.evidence import append_row  # noqa: E402
from crbench.runner import load_run  # noqa: E402

LEDGER = os.path.join(PROJ, "EVIDENCE.md")
KS = (4, 8, 12, 16, 24, 32, 48, 64)
HEAD = """# EVIDENCE — every number in the paper traces to a log

> Owner: `experimenter`. Rebuilt by `code/ledger.py` from raw logs; audited by `falsifier` and by
> `crbench audit-tex`. Machine: one laptop core (hashed host in each row); date = date of the run.
> Times are pure-Python toy CPU times: only ratios between arms are printed in the paper.

"""


def code_hash() -> str:
    path = os.path.join(PROJ, "results", "CODE-SHA256.txt")
    import hashlib
    return "code:" + hashlib.sha256(open(path, "rb").read()).hexdigest()[:10]


def counts() -> dict:
    out = {}
    for line in open(os.path.join(PROJ, "results", "counts", "counts.log")):
        if line.startswith("{"):
            d = json.loads(line)
            out[d["k"]] = d
    return out


def soundness_bits(name: str) -> str:
    t = open(os.path.join(PROJ, "results", "soundness", name + ".txt")).read()
    return re.search(r"\*\*Security level: ([\d.]+) bits", t).group(1)


HOST = "host:" + capture_env()["host_id"] + " / 1 thr"


def add(rid, printed, command, log, runs, machine=HOST, date=None):
    append_row(LEDGER, printed, command, log, commit=code_hash(), machine=machine, date=date, runs=runs, id=rid)


def main() -> int:
    with open(LEDGER, "w") as f:
        f.write(HEAD)
    c = counts()
    ver = c[64]["version"]
    cnt_cmd, cnt_log = "python3 circuits/count.py", "results/counts/counts.log"
    # --- counts (deterministic) ---
    add("E1", f"Table 1 (counts, circuits {ver}, n = 64, c = 8, k in {{4..64}})", cnt_cmd, cnt_log, "1 / exact")
    add("E2", f"{c[64]['r1cs']['constraints']} constraints", cnt_cmd + "  (R1CS bits, k = 64)", cnt_log, "1 / exact")
    add("E3", f"{c[64]['bits']['height_pow2']} rows", cnt_cmd + "  (bits arm, padded height, k = 64)", cnt_log, "1 / exact")
    add("E4", f"{c[64]['lookup']['height_pow2']} rows", cnt_cmd + "  (lookup arm, padded height, k = 64)", cnt_log, "1 / exact")
    for rid, k in (("E5", 4), ("E6", 8), ("E7", 16)):
        r = c[k]["bits"]["height_pow2"] / c[k]["lookup"]["height_pow2"]
        add(rid, f"{r:g}×", cnt_cmd + f"  (padded-height ratio bits/lookup, k = {k})", cnt_log, "1 / exact")
    add("E8", f"{c[64]['lookup']['table_rows']} rows", cnt_cmd + "  (logUp table [0, 2^8))", cnt_log, "1 / exact")
    # --- prover time ratios (raw samples from run.json) ---
    run_path = os.path.join(PROJ, "results", "bench_kscan", "run.json")
    if os.path.exists(run_path):
        run = load_run(run_path)
        date = run.started[:10]
        for i, k in enumerate(KS):
            sp = stats.speedup(run.samples(f"bits_k{k}"), run.samples(f"lookup_k{k}"), paired=True)
            n = len(run.samples(f"bits_k{k}"))
            add(f"E{10 + i}", f"{sp.ratio:.2f}×",
                f"python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = {k}; "
                f"paired bootstrap 95% CI [{sp.ci_low:.2f}, {sp.ci_high:.2f}])",
                "results/bench_kscan/run.json", f"{n} interleaved / median", date=date)
    # --- falsifier's edge runs (limb width, statement size), added after review item A-W2 (DECISIONS D-8) ---
    edge = os.path.join(PROJ, "results", "falsify_C4_edges", "run.json")
    if os.path.exists(edge):
        er = load_run(edge)
        for rid, base, cand, what in (("E40", "bits_n64_k32", "lookup_c4_n64_k32", "c = 4, n = 64, k = 32"),
                                      ("E41", "bits_n64_k32", "lookup_c8_n64_k32", "c = 8, n = 64, k = 32"),
                                      ("E42", "bits_n64_k32", "lookup_c16_n64_k32", "c = 16, n = 64, k = 32"),
                                      ("E43", "bits_n16_k16", "lookup_c8_n16_k16", "c = 8, n = 16, k = 16")):
            sp = stats.speedup(er.samples(base), er.samples(cand), paired=True)
            add(rid, f"{sp.ratio:.2f}×", f"python3 falsify/C4_time/edges.py  (median CPU-time ratio bits/lookup, {what}; "
                f"paired bootstrap 95% CI [{sp.ci_low:.2f}, {sp.ci_high:.2f}])", "results/falsify_C4_edges/run.json",
                f"{len(er.samples(base))} interleaved / median", date=er.started[:10])
    # --- soundness (soundness_calc outputs) ---
    for rid, arm, lvl in (("E20", "lookup", "worst-case"), ("E21", "lookup", "average-case"),
                          ("E22", "bits", "worst-case"), ("E23", "bits", "average-case")):
        nm = f"{arm}_k64_{lvl}"
        add(rid, f"{soundness_bits(nm)} bits", f"python3 theory/budget.py  ({arm} arm, k = 64, {lvl}, proven)",
            f"results/soundness/{nm}.txt", "1 / exact", machine="n/a (exact computation)")
    # --- falsifier findings (deterministic logs) ---
    flog = "falsify/C1_lookup_circuit/audit.log"
    if os.path.exists(os.path.join(PROJ, flog)):
        t = open(os.path.join(PROJ, flog)).read()
        m = re.search(r"buggy v1 .*?accepts out-of-spec \[([\d, ]+)\]", t)
        add("E30", f"accepts {m.group(1).split(',')[0]} (k = 3, c = 2, F_11)",
            "python3 falsify/C1_lookup_circuit/audit.py  (exhaustive, circuits v1)", flog, "1 / exact", machine="n/a (exact computation)")
        m = re.search(r"real field: v1 accepts x = (2\^\d+)", t)
        add("E31", f"{m.group(1)}", "python3 falsify/C1_lookup_circuit/audit.py  (Goldilocks witness, circuits v1, k = 12)",
            flog, "1 / exact", machine="n/a (exact computation)")
    flog = "falsify/C5_fs/attack.log"
    if os.path.exists(os.path.join(PROJ, flog)):
        t = open(os.path.join(PROJ, flog)).read()
        m = re.search(r"v1 transcript: forged proofs accepted (\d+)/(\d+)", t)
        add("E32", f"{m.group(1)}/{m.group(2)} forged proofs accepted",
            "python3 falsify/C5_fs/attack.py  (prover v1)", flog, "1 / exact", machine="n/a (exact computation)")
    r = subprocess.run([sys.executable, "-m", "crbench", "evidence", "check", "EVIDENCE.md", "--root", "."],
                       cwd=PROJ, capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": os.path.join(PROJ, "..", "..", "lib", "bench")})
    print(r.stdout + r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
