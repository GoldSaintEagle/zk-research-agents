# SNAPSHOT of circuits/range_gadgets.py as audited at P6 (circuits v1, before the fix of DECISIONS D-5). Do not edit.
# TOY: not secure -- range-check gadgets for a teaching example; small fields and a toy prover only.
"""Range-check gadgets (owner: circuit-engineer). Specifications: circuits/range_bits/SPEC.md and
circuits/range_lookup/SPEC.md.

Three encodings of "x_j < 2^k for the public values x_1..x_n", all built over a prime field F_p given as a
parameter (Goldilocks for the experiments, F_11 / F_17 for the exhaustive audits):

  r1cs_bits      R1CS: k booleanity constraints b(b - 1) = 0 and one recomposition per value
                 ([Thaler §6.5.4, Details of the Transformation]);
  plonk_bits     Plonkish, one advice column `acc`, k + 1 rows per value, MSB first: acc_0 = 0 (gate `zero`),
                 acc_{i+1} = 2 acc_i + b with (acc_{i+1} - 2 acc_i)(acc_{i+1} - 2 acc_i - 1) = 0 (gate `runsum`,
                 degree 2), the last acc copied to the public x_j;
  plonk_lookup   Plonkish + lookups, advice columns `acc`, `limb`, L + 1 rows per value (L = ceil(k / c)), MSB
                 first: acc_0 = 0 (gate `zero`), acc_{i+1} = 2^c acc_i + limb_i (gate `limb`, degree 1), every
                 limb looked up in the fixed table [0, 2^c), the last acc copied to x_j
                 ([Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields]).

The builders take the public values and produce the honest witness with the generator `limbs_msb_first`; the
generator refuses out-of-range inputs. Counts are read off the built objects (`counts`), never typed in.
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "..", "..", "lib", "cryptomath")
if LIB not in sys.path:
    sys.path.insert(0, LIB)
from cryptomath.zk.plonkish import Plonkish, next_pow2  # noqa: E402
from cryptomath.zk.r1cs import R1CS  # noqa: E402

GOLDILOCKS = 2 ** 64 - 2 ** 32 + 1
VERSION = "v1"


def limbs_msb_first(x: int, k: int, c: int) -> list[int]:
    """Witness generator: the ceil(k / c) base-2^c digits of x, most significant first."""
    if not 0 <= x < 2 ** k:
        raise ValueError(f"x = {x} is not a {k}-bit value")
    L = math.ceil(k / c)
    return [(x >> (c * i)) & (2 ** c - 1) for i in reversed(range(L))]


def r1cs_bits(xs: list[int], k: int, p: int = GOLDILOCKS) -> tuple[R1CS, dict]:
    cs, z = R1CS(p), {"one": 1}
    for j, x in enumerate(xs):
        bits = limbs_msb_first(x, k, 1)[::-1]             # LSB first
        names = [f"b{j}_{i}" for i in range(k)]
        cs.public.append(f"x{j}")
        cs.witness += names
        z[f"x{j}"] = x
        z.update(zip(names, bits))
        for b in names:
            cs.add({b: 1}, {b: 1, "one": -1}, {}, f"bool[{b}]")
        cs.add({"one": 1}, {b: pow(2, i, p) for i, b in enumerate(names)}, {f"x{j}": 1}, f"recompose[{j}]")
    return cs, z


def plonk_bits(xs: list[int], k: int, p: int = GOLDILOCKS) -> Plonkish:
    gates = {"zero": (1, lambda cur, _: cur["acc"]),
             "runsum": (2, lambda cur, nxt: (nxt["acc"] - 2 * cur["acc"]) * (nxt["acc"] - 2 * cur["acc"] - 1))}
    t = Plonkish(1, gates)
    for j, x in enumerate(xs):
        bits = limbs_msb_first(x, k, 1)
        acc = 0
        for i, b in enumerate(bits):
            t.rows.append((("zero", "runsum") if i == 0 else ("runsum",), {"acc": acc}))
            acc = 2 * acc + b
        t.rows.append(((), {"acc": acc}))
        t.copies.append(((len(t.rows) - 1, "acc"), ("pub", j)))
    return t


def plonk_lookup(xs: list[int], k: int, c: int = 8, p: int = GOLDILOCKS) -> Plonkish:
    gates = {"zero": (1, lambda cur, _: cur["acc"]),
             "limb": (1, lambda cur, nxt: nxt["acc"] - (2 ** c) * cur["acc"] - cur["limb"])}
    t = Plonkish(2, gates, table=range(2 ** c))
    for j, x in enumerate(xs):
        acc = 0
        for i, limb in enumerate(limbs_msb_first(x, k, c)):
            row = len(t.rows)
            t.rows.append((("zero", "limb") if i == 0 else ("limb",), {"acc": acc, "limb": limb}))
            t.lookups.append((row, "limb", 1))           # limb in [0, 2^c)
            acc = (2 ** c) * acc + limb
        t.rows.append(((), {"acc": acc}))
        t.copies.append(((len(t.rows) - 1, "acc"), ("pub", j)))
    return t


def build(arm: str, xs: list[int], k: int, c: int = 8, p: int = GOLDILOCKS):
    if arm == "bits":
        return plonk_bits(xs, k, p)
    if arm == "lookup":
        return plonk_lookup(xs, k, c, p)
    raise ValueError(arm)


def counts(arm: str, n: int, k: int, c: int = 8) -> dict:
    """Counts of the circuit for n values (built on in-range dummy inputs; the structure does not depend on x)."""
    xs = [(2 ** k - 1) * (j % 2) for j in range(n)]
    if arm == "r1cs":
        return r1cs_bits(xs, k)[0].counts()
    out = build(arm, xs, k, c).counts()
    out["height_pow2"] = next_pow2(out["height"])
    return out


if __name__ == "__main__":
    xs = [0, 1, 2 ** 12 - 1, 1234]
    for arm in ("bits", "lookup"):
        assert build(arm, xs, 12).satisfied(xs), arm
    cs, z = r1cs_bits(xs, 12)
    assert cs.satisfied(z)
    print("range_gadgets", VERSION, "OK", counts("lookup", 64, 12))
