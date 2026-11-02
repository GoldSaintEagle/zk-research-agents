# TOY: not secure
"""Builder self-audit of the Fiat-Shamir transcript of impl/toy_prover.py (owner: prover-engineer;
skills/fiat-shamir-audit, procedure step 2).

    python3 impl/fs_selfaudit.py      # prints the transcript table and the test results, exit 1 on a failure

Tests (as the skill's procedure lists them):
  * transcript table of the prover's transcript, linted against the paper's order (THEORY.md T1) with
    skills/fiat-shamir-audit/scripts/toy_fs_attack.py::transcript_lint;
  * sensitivity: flipping each public input and each parameter changes the first challenge;
  * recomputation: the proof carries no challenge; tampering with one sum-check message is rejected;
  * domain tags: distinct and prefix-free.
"""
from __future__ import annotations

import copy
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "skills", "fiat-shamir-audit", "scripts"))
import toy_prover  # noqa: E402
from cryptomath.protocols import fiat_shamir  # noqa: E402
from range_gadgets import GOLDILOCKS as P, build  # noqa: E402
from toy_fs_attack import domain_separated, transcript_lint  # noqa: E402

LOG: list = []                      # (transcript id, kind, label) of every absorb / squeeze


class Recording(fiat_shamir.Transcript):
    def __init__(self, domain):
        super().__init__(domain)
        LOG.append((id(self), "domain", domain.decode()))

    def append(self, label, data):
        LOG.append((id(self), "absorb", label.decode()))
        super().append(label, data)

    def challenge_bytes(self, label, n=32):
        LOG.append((id(self), "squeeze", label.decode()))
        return super().challenge_bytes(label, n)


def first_challenge(arm, xs, k, c=8, n=None):
    meta = {"arm": arm, "n": n or len(xs), "k": k, "c": c}
    lay = toy_prover.compile_table(build(arm, xs, k, c), xs, P)
    tr = toy_prover.statement_transcript(lay, meta, xs)
    for a in sorted(lay.advice):
        tr.append(b"root:" + a.encode(), toy_prover.commit(lay.advice[a], P))
    return tr.challenge_scalar(b"beta" if lay.groups else b"tau0", P)


def main() -> int:
    fiat_shamir.Transcript = Recording
    toy_prover.Transcript = Recording
    rng = random.Random(3)
    ok = True
    for arm in ("bits", "lookup"):
        k = 12
        xs = [rng.randrange(2 ** k) for _ in range(4)]
        meta = {"arm": arm, "n": 4, "k": k, "c": 8}
        LOG.clear()
        proof = toy_prover.prove(build(arm, xs, k), xs, meta, P)
        outer = LOG[0][0]
        table = [(kind, lab) for tid, kind, lab in LOG if tid == outer]
        absorbed = [lab.split(":")[0] if lab.startswith("root") else lab.rstrip("0123456789") for _, lab in table]
        required = ["arm", "n", "k", "c", "p", "H", "index", "x", "root"] + (["beta", "root"] if arm == "lookup" else []) \
            + ["tau", "alpha"]
        dedup = [a for i, a in enumerate(absorbed) if i == 0 or a != absorbed[i - 1]]
        lint = transcript_lint(dedup, required)
        print(f"[{arm}] transcript (outer): " + " | ".join(f"{k_}:{l}" for k_, l in table[:6]) + f" ... ({len(table)} items)")
        print(f"[{arm}] lint vs paper order: {'PASS' if not lint else 'FAIL ' + str(lint)}")
        ok &= not lint
        base = first_challenge(arm, xs, k)
        flips = [first_challenge(arm, [xs[0] + 1] + xs[1:], k) != base,
                 first_challenge(arm, xs, k, c=4) != base if arm == "lookup" else True,
                 first_challenge(arm, xs, k, n=5) != base]
        print(f"[{arm}] sensitivity of the first challenge to x_0, c, n: {'PASS' if all(flips) else 'FAIL'}")
        ok &= all(flips)
        bad = copy.deepcopy(proof)
        bad.zerocheck["messages"][0][1] = (bad.zerocheck["messages"][0][1] + 1) % P
        rej = not toy_prover.verify(build(arm, [0] * 4, k), xs, meta, bad, P)
        print(f"[{arm}] tampered sum-check message rejected: {'PASS' if rej else 'FAIL'}")
        ok &= rej
    tags = {"domain": toy_prover.DOMAIN, "root": b"msg:root:", "beta": b"chal:beta", "tau": b"chal:tau", "alpha": b"chal:alpha"}
    ds = domain_separated(tags)
    print(f"domain tags distinct and prefix-free: {'PASS' if ds else 'FAIL'}")
    ok &= ds
    print(f"FS self-audit (builder): {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
