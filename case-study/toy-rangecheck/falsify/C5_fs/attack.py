#!/usr/bin/env python3
# TOY: not secure
"""Falsifier's independent Fiat-Shamir audit of the toy prover (skills/fiat-shamir-audit; attack order step 3).

    python3 falsify/C5_fs/attack.py > falsify/C5_fs/attack.log

1. Sensitivity of EVERY challenge (not only the first): flip the public input x_0 and list which challenges
   change. A challenge that does not move is derived from a transcript that does not contain the statement.
2. The attack that this enables ([CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness]):
   if the zero-check challenges r_1..r_v do not depend on the statement or the commitments, the prover can fix
   them first (all-zero sum-check messages give a known point r*), then choose a FALSE statement and columns
   that pass the final check at r*: acc = 0 everywhere and public inputs with pub~(r*) = 0, one of them 2^k.
3. The same forgery against the current prover (after the fix of DECISIONS D-6) must be rejected.
Runs on the frozen v1 snapshot (toy_prover_v1.py next to this file) and on impl/toy_prover.py.
"""
from __future__ import annotations

import importlib.util
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(PROJ, "..", ".."))
sys.path[:0] = [os.path.join(REPO, "lib", "cryptomath"), os.path.join(PROJ, "circuits"), os.path.join(PROJ, "impl")]
from cryptomath.protocols import fiat_shamir  # noqa: E402
from cryptomath.zk import sumcheck  # noqa: E402
from cryptomath.zk.mle import eq_table  # noqa: E402
from range_gadgets import GOLDILOCKS as P, build  # noqa: E402


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


V1 = load(os.path.join(HERE, "toy_prover_v1.py"), "toy_prover_v1")
CUR = load(os.path.join(PROJ, "impl", "toy_prover.py"), "toy_prover_cur")

SQUEEZED: list = []


class Rec(fiat_shamir.Transcript):
    def challenge_bytes(self, label, n=32):
        out = super().challenge_bytes(label, n)
        SQUEEZED.append((label.decode(), out))
        return out


def verifier_challenges(mod, arm, xs_proof, xs_claimed, k):
    """Challenges the VERIFIER derives for one fixed proof (made for xs_proof) when the statement is xs_claimed."""
    meta = {"arm": arm, "n": len(xs_proof), "k": k, "c": 8}
    proof = mod.prove(build(arm, xs_proof, k), xs_proof, meta, P)
    SQUEEZED.clear()
    saved = (mod.Transcript, fiat_shamir.Transcript)
    mod.Transcript = fiat_shamir.Transcript = Rec     # the lib's sum-check builds its transcript through this name
    try:
        mod.verify(build(arm, [0] * len(xs_proof), k), xs_claimed, meta, proof, P)
    finally:
        mod.Transcript, fiat_shamir.Transcript = saved
    seen, out = {}, {}
    for lab, val in SQUEEZED:                       # zero-check and grand-sum both squeeze r0, r1, ...
        seen[lab] = seen.get(lab, 0) + 1
        out[lab if seen[lab] == 1 else f"{lab}(grandsum)"] = val
    return out


def sensitivity(mod, name):
    """Same prover messages, two statements: every challenge must change (skills/fiat-shamir-audit item 1, applied
    to every challenge, sub-protocols included)."""
    rng = random.Random(5)
    for arm in ("bits", "lookup"):
        k = 8
        xs = [rng.randrange(2 ** k) for _ in range(4)]
        a = verifier_challenges(mod, arm, xs, xs, k)
        b = verifier_challenges(mod, arm, xs, [(xs[0] + 1) % 2 ** k] + xs[1:], k)
        same = sorted(lab for lab in a if a[lab] == b.get(lab))
        print(f"[{name}] {arm}: {len(a)} challenges; unchanged when only the statement changes: "
              f"{same if same else 'none'}")


def forge(mod, arm: str, k: int, n: int = 4):
    """A proof for a false statement (x_0 = 2^k) when the zero-check transcript ignores the statement."""
    xs0 = [0] * n
    lay = mod.compile_table(build(arm, xs0, k), xs0, P)
    v = lay.H.bit_length() - 1
    tables_dummy, _, d = mod.zerocheck_tables(lay, lay.advice, mod.logup_helpers(lay, lay.advice, 1) if lay.groups else {},
                                              1, [0] * v, 1)
    # the challenges the verifier will derive from all-zero messages, computed BEFORE choosing the statement
    zero_msgs = [[0] * (d + 1) for _ in range(v)]
    t = sumcheck._transcript(v, d, P, 0, b"zerocheck")
    rstar = []
    for j, m in enumerate(zero_msgs):
        for i, y in enumerate(m):
            t.append(b"s%d_%d" % (j, i), y.to_bytes(8, "big"))
        rstar.append(t.challenge_scalar(b"r%d" % j, P))
    # choose the statement: x_0 = 2^k (false), x_1 such that pub~(r*) = 0
    eqr = eq_table(rstar, P)
    pub_rows = [r for (r, _c), _b in sorted(build(arm, xs0, k).copies, key=lambda c: c[1][1])]
    xs = [0] * n
    xs[0] = 2 ** k
    xs[1] = (-xs[0] * eqr[pub_rows[0]] * pow(eqr[pub_rows[1]], P - 2, P)) % P
    # columns: everything zero (acc = 0; for the lookup arm also limb = 0, m and helpers chosen to pass)
    lay = mod.compile_table(build(arm, xs0, k), xs, P)
    adv = {a: [0] * lay.H for a in lay.advice}
    meta = {"arm": arm, "n": n, "k": k, "c": 8}
    tr = mod.statement_transcript(lay, meta, xs)
    roots = {a: mod.commit(adv[a], P) for a in sorted(adv)}
    for a in sorted(adv):
        tr.append(b"root:" + a.encode(), roots[a])
    helpers, hroots, gs = {}, {}, None
    if lay.groups:
        beta = tr.challenge_scalar(b"beta", P)
        adv["m"] = [0] * lay.H
        adv["m"][0] = sum(len([1 for _ in range(lay.H) if lay.fixed[f"qlk:{c}:{s}"][_]]) for c, s in lay.groups)
        roots["m"] = mod.commit(adv["m"], P)
        helpers = mod.logup_helpers(lay, adv, beta)       # honest helpers for the all-zero limbs
        hroots = {h: mod.commit(col, P) for h, col in sorted(helpers.items())}
        hs, gcomb = mod.grandsum(lay, helpers)
        gs = sumcheck.prove_fs(hs, P, label=b"grandsum", combine=gcomb, degree=1)
    proof = mod.Proof(roots, hroots, {"claim": 0, "messages": zero_msgs, "v": v, "d": d}, gs,
                      oracle={**adv, **helpers})
    return mod.verify(build(arm, xs0, k), xs, meta, proof, P), xs


def main() -> int:
    sensitivity(V1, "v1")
    sensitivity(CUR, "current")
    for name, mod in (("v1", V1), ("current", CUR)):
        wins, total, example = 0, 0, None
        for arm in ("bits",):
            for k in (4, 8, 12, 16):
                ok, xs = forge(mod, arm, k)
                wins += ok
                total += 1
                example = example or (ok and (arm, k, xs[0]))
        print(f"{name} transcript: forged proofs accepted {wins}/{total} (false statements with x_0 = 2^k, bits arm, "
              f"k in {{4, 8, 12, 16}}){'; e.g. ' + str(example) if example else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
