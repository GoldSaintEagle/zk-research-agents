# TOY: not secure
"""P5 driver (owner: experimenter). Runs every experiment through crbench and writes logs under results/.

    python3 code/run_experiments.py                    # counts + bench_kscan (~1.5 min), then sanitise
    python3 code/run_experiments.py --only counts      # one experiment
    python3 code/run_experiments.py --sanitise-only    # scrub home dir / user / hostname / proxy from results/
    python3 code/run_experiments.py --only bench_kscan --out results-rerun   # re-measure without touching results/

Experiments
  counts       circuits/count.py (the toy's "compiler output") -> results/counts/counts.log   (deterministic)
  bench_kscan  impl/prove.py, bits vs lookup arm, n = 64, c = 8, k in {4, 8, 12, 16, 24, 32, 48, 64};
               all 16 arms in ONE interleaved session (rotating order), 1 warm-up + 7 rounds, threads = 1;
               metric: process CPU time of build + prove ("prove time"); every execution verifies its proof
               (exit 1 otherwise -> crbench failure) -> results/bench_kscan/{run.json, <arm>/r*.log, summary.log}

Protocol: results/bench_kscan/README.md (fixed before the first run). Statistics: crbench.stats (median, IQR,
paired bootstrap CI of the ratio bits/lookup).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "..", "..", "lib", "bench"))
from crbench import stats  # noqa: E402
from crbench.runner import run_interleaved  # noqa: E402

PY = sys.executable
RES = os.path.join(PROJ, "results")
KS = (4, 8, 12, 16, 24, 32, 48, 64)
os.environ.pop("LD_LIBRARY_PATH", None)


def fresh_dir(d):
    """Move a previous run of the same experiment out of the way (to a temp dir, not deleted)."""
    if os.path.exists(d):
        shutil.move(d, tempfile.mkdtemp(prefix="old_" + os.path.basename(d) + "_"))
    os.makedirs(d)


def exp_counts():
    d = os.path.join(RES, "counts")
    os.makedirs(d, exist_ok=True)
    out = subprocess.run([PY, "circuits/count.py"], cwd=PROJ, capture_output=True, text=True, check=True).stdout
    with open(os.path.join(d, "counts.log"), "w") as f:
        f.write(f"# cmd: python3 circuits/count.py\n{out}")
    print(out)


def bench(name, arms, repeats=7, warmup=1):
    d = os.path.join(RES, name)
    keep = os.path.join(d, "README.md")
    readme = open(keep).read() if os.path.exists(keep) else None
    fresh_dir(d)
    if readme:
        with open(keep, "w") as f:
            f.write(readme)
    r = run_interleaved(arms, repeats=repeats, warmup=warmup, order="alternate", parser="generic", metric="time",
                        label="prove", log_dir=os.path.relpath(d, PROJ), threads=1, cwd=PROJ, target_dir=PROJ,
                        verbose=True)
    return r, d


def exp_kscan(n=64, c=8, ks=KS, name="bench_kscan"):
    arms = {}
    for k in ks:
        for arm in ("bits", "lookup"):
            arms[f"{arm}_k{k}"] = f"{PY} impl/prove.py --arm {arm} --k {k} --n {n} --c {c}"
    r, d = bench(name, arms)
    s = r.summary()
    out = [f"# {name}: toy prover CPU time (build + prove), n = {n}, c = {c}, Goldilocks, pure Python, 1 thread",
           f"# rounds={r.repeats} warmup={r.warmup} order={r.order} started={r.started} finished={r.finished}"]
    for k in ks:
        b, l = f"bits_k{k}", f"lookup_k{k}"
        sp = stats.speedup(r.samples(b), r.samples(l), paired=True)
        out.append(f"k={k} bits_median_ms={1e3 * s[b]['median']:.2f} bits_iqr_ms={1e3 * s[b]['iqr']:.2f} "
                   f"lookup_median_ms={1e3 * s[l]['median']:.2f} lookup_iqr_ms={1e3 * s[l]['iqr']:.2f} "
                   f"ratio_bits_over_lookup={sp.fmt(2)} failures={s[b]['failures'] + s[l]['failures']}")
    write_summary(d, out)


def write_summary(d, lines):
    with open(os.path.join(d, "summary.log"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def code_hashes():
    lines = []
    for sub in ("circuits", "impl", "code", "theory"):
        for fn in sorted(os.listdir(os.path.join(PROJ, sub))):
            if fn.endswith(".py"):
                h = hashlib.sha256(open(os.path.join(PROJ, sub, fn), "rb").read()).hexdigest()[:16]
                lines.append(f"{h}  {sub}/{fn}")
    with open(os.path.join(RES, "CODE-SHA256.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


def sanitise(root):
    """Replace the home directory, the user name, the host name and proxy addresses in every text file."""
    home = os.path.expanduser("~")
    user = os.path.basename(home)
    host = platform.node()
    proxies = {os.environ.get(v) for v in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy")} - {None, ""}
    for dp, _dn, fns in os.walk(root):
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                t = open(p).read()
            except UnicodeDecodeError:
                continue
            u = t.replace(home, "~").replace(sys.prefix, "<venv>")
            for px in proxies:
                u = u.replace(px, "<proxy>")
            if host:
                u = u.replace(host, "host")
            u = re.sub(rf"\b{re.escape(user)}\b", "user", u) if user else u
            u = re.sub(r"/private/tmp/[^\s\"']*", "<tmp>", u)
            if u != t:
                open(p, "w").write(u)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=["counts", "bench_kscan"])
    ap.add_argument("--sanitise-only", action="store_true")
    ap.add_argument("--out", default="results", help="results directory relative to the project (default results/)")
    a = ap.parse_args(argv)
    global RES
    RES = os.path.join(PROJ, a.out)
    if not a.sanitise_only:
        if a.only in (None, "counts"):
            exp_counts()
        if a.only in (None, "bench_kscan"):
            exp_kscan()
        if a.out == "results":
            code_hashes()
    sanitise(RES)
    return 0


if __name__ == "__main__":
    sys.exit(main())
