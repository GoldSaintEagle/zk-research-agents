"""Abstract operation counting.

Use it to *screen ideas before implementing them*: write the algorithm once
in plain Python against abstract operations, run it under a ``Counter`` and
compare the counts (or a weighted cost) with a baseline.

    from cryptomath.costmodel import Counter, count, counted, MSM, HASH

    @counted(HASH)
    def compress(l, r): return hash((l, r))

    with Counter() as c:
        compress(1, 2)
        count(MSM, 3)
    c.counts  # {'hash': 1, 'msm': 3}

Counters nest: every active counter on the stack sees every event, so an
outer counter can total a whole prover while inner ones measure phases.
When no counter is active, :func:`count` is a cheap no-op, so library code
(the toy proof-system components in ``cryptomath.zk``) can call it
unconditionally.

Standard op names are module constants (strings) so reports line up; the
ZK names are the ones skills/prover-cost-model prints.

This module is stdlib-only (no sympy, no numpy), so skill scripts can use it
with a bare Python.
"""
from __future__ import annotations

import functools
import threading
from collections import Counter as _PyCounter
from typing import Callable, Dict, Iterable, List, Optional

__all__ = [
    "MUL", "SMULT", "ADD", "FMUL", "FADD", "FINV", "NTT", "BFLY", "MSM", "MSM_PTS", "GADD",
    "PAIR", "HASH", "SC_ROUND", "SC_TERM", "MEM", "CONSTRAINT", "LOOKUP",
    "Counter", "count", "counted", "note_depth", "active_counters", "DEFAULT_WEIGHTS",
]

# generic arithmetic (used by Traced): a nonlinear multiplication is one R1CS constraint
MUL = "mult"               # multiplication of two non-constant values
SMULT = "scalar_mult"      # multiplication by a constant (free in R1CS / linear in Plonkish)
ADD = "add"
# field and group operations of a prover / verifier
FMUL = "field_mult"
FADD = "field_add"
FINV = "field_inv"
NTT = "ntt"                # one NTT / FFT call (its size is in the butterfly count)
BFLY = "ntt_butterfly"     # radix-2 butterfly (one mult + two adds)
MSM = "msm"                # one multi-scalar multiplication call
MSM_PTS = "msm_points"     # total points over all MSMs
GADD = "group_add"         # elliptic-curve group additions (Pippenger buckets + reductions)
PAIR = "pairing"
HASH = "hash"              # one compression (Merkle node, leaf, transcript squeeze)
SC_ROUND = "sumcheck_round"
SC_TERM = "sumcheck_term"  # one evaluation of the summand g at a partially bound point
MEM = "mem_bytes"          # estimated memory traffic
CONSTRAINT = "constraint"  # R1CS constraint / Plonkish gate row
LOOKUP = "lookup"

# Rough relative weights, unit = one ~256-bit field multiplication.  Replace
# with measured numbers from lib/bench (one EVIDENCE row each) before drawing
# conclusions; skills/prover-cost-model keeps per-field nanosecond units.
DEFAULT_WEIGHTS: Dict[str, float] = {
    MUL: 1.0, SMULT: 1.0, ADD: 0.1, FMUL: 1.0, FADD: 0.1, FINV: 50.0,
    NTT: 0.0, BFLY: 1.3, MSM: 0.0, MSM_PTS: 0.0, GADD: 12.0, PAIR: 3e4,
    HASH: 8.0, SC_ROUND: 0.0, SC_TERM: 2.0, MEM: 0.0, CONSTRAINT: 0.0, LOOKUP: 0.0,
}

_local = threading.local()


def active_counters() -> List["Counter"]:
    if not hasattr(_local, "stack"):
        _local.stack = []
    return _local.stack


class Counter:
    """Context manager accumulating op counts (and optional max depth)."""

    def __init__(self, name: str = ""):
        self.name = name
        self.counts: _PyCounter = _PyCounter()
        self.max_depth = 0

    def __enter__(self) -> "Counter":
        active_counters().append(self)
        return self

    def __exit__(self, *exc):
        st = active_counters()
        if st and st[-1] is self:
            st.pop()
        else:  # pragma: no cover - defensive
            st.remove(self)
        return False

    def add(self, op: str, n: int = 1) -> None:
        self.counts[op] += n

    def note_depth(self, d: int) -> None:
        if d > self.max_depth:
            self.max_depth = d

    def __getitem__(self, op: str) -> int:
        return self.counts.get(op, 0)

    def total(self, weights: Optional[Dict[str, float]] = None) -> float:
        w = DEFAULT_WEIGHTS if weights is None else weights
        return sum(w.get(op, 0.0) * n for op, n in self.counts.items())

    def as_dict(self) -> Dict[str, int]:
        d = dict(self.counts)
        if self.max_depth:
            d["depth"] = self.max_depth
        return d

    def __repr__(self):
        return f"Counter({self.name!r}, {self.as_dict()})"


def count(op: str, n: int = 1) -> None:
    """Record ``n`` occurrences of ``op`` in every active counter."""
    for c in active_counters():
        c.add(op, n)


def note_depth(d: int) -> None:
    for c in active_counters():
        c.note_depth(d)


def counted(op: str, n: int = 1) -> Callable:
    """Decorator: each call of the function records ``n`` x ``op``."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            count(op, n)
            return fn(*a, **kw)
        return wrapper
    return deco
