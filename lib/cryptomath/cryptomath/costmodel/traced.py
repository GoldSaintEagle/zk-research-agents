"""``Traced`` values: run ordinary arithmetic code and get op counts + depth.

A :class:`Traced` wraps an (optional) concrete value.  Arithmetic between two
Traced values is a *nonlinear* multiplication (``mult``) and increases
multiplicative depth; arithmetic with plain numbers is a scalar operation.
Every operation is reported to the active :class:`~cryptomath.costmodel.Counter`.

For a straight-line computation over a prime field this is the R1CS view: one
nonlinear multiplication = one rank-1 constraint, additions and constant
multiplications are free ([Thaler §8.4, Extension from Circuit-SAT to R1CS-SAT]);
the depth bounds the degree of the arithmetic circuit (degree <= 2^depth).
Count a gadget before writing it in a circuit DSL:

    from cryptomath.costmodel import Counter, Traced
    with Counter() as c:
        x = Traced(3)
        y = x ** 5 + 7 * x          # Poseidon-style S-box plus a linear term
    c['mult'], y.depth, y.value     # (3, 3, 264)
"""
from __future__ import annotations

from typing import Any, Optional

from .counter import ADD, MUL, SMULT, count, note_depth

__all__ = ["Traced"]


class Traced:
    __slots__ = ("value", "depth")

    def __init__(self, value: Any = None, depth: int = 0):
        self.value = value
        self.depth = depth

    def _new(self, value, depth):
        note_depth(depth)
        return Traced(value, depth)

    @staticmethod
    def _v(x):
        return x.value if isinstance(x, Traced) else x

    def _combine(self, other, fn):
        a, b = self.value, self._v(other)
        if a is None or b is None:
            return None
        return fn(a, b)

    # additive ops: free in depth (and free in R1CS)
    def __add__(self, o):
        count(ADD)
        d = max(self.depth, o.depth) if isinstance(o, Traced) else self.depth
        return self._new(self._combine(o, lambda a, b: a + b), d)

    __radd__ = __add__

    def __sub__(self, o):
        count(ADD)
        d = max(self.depth, o.depth) if isinstance(o, Traced) else self.depth
        return self._new(self._combine(o, lambda a, b: a - b), d)

    def __rsub__(self, o):
        count(ADD)
        return self._new(self._combine(o, lambda a, b: b - a), self.depth)

    def __neg__(self):
        return self._new(None if self.value is None else -self.value, self.depth)

    def __mul__(self, o):
        if isinstance(o, Traced):
            count(MUL)
            return self._new(self._combine(o, lambda a, b: a * b), max(self.depth, o.depth) + 1)
        if o == 0:
            return self._new(0 * self.value if self.value is not None else None, 0)
        count(SMULT)
        return self._new(self._combine(o, lambda a, b: a * b), self.depth)

    __rmul__ = __mul__

    def __pow__(self, e: int):
        """Square-and-multiply (counts its own multiplications)."""
        if e < 1:
            raise ValueError("positive exponents only")
        result, base = None, self
        while e:
            if e & 1:
                result = base if result is None else result * base
            e >>= 1
            if e:
                base = base * base
        return result

    def __repr__(self):
        return f"Traced({self.value!r}, depth={self.depth})"
