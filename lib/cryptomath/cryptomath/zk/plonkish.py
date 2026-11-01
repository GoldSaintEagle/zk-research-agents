# TOY: not secure -- a table checked in the clear; for counting rows / columns and testing gadgets.
"""Plonkish constraint systems: a table of advice cells with gates, copy constraints and lookups.

A Plonkish circuit is a rectangular table. Each row enables some named gates
(polynomial identities over the current and the next row), copy constraints
equate cells (enforced in a real prover by the permutation argument of
:mod:`cryptomath.zk.plonk`), and lookups require a cell -- optionally scaled --
to appear in a fixed table column (enforced by e.g. logUp, also in
:mod:`cryptomath.zk.plonk`). Columns, rows, degree and lookups are what the
prover pays for: the trace is padded to a power of two at least the number of
used rows and at least the table size, and the quotient degree grows with the
gate degree ([Thaler §19.3.3, Intermediate Representations (IRs) Other than Arithmetic Circuits and R1CS]).

Counts (:meth:`Plonkish.counts`) follow skills/constraint-cost and CIRCUITS.md:
rows used, height (max of rows and table size), height padded to a power of
two, advice / fixed columns, max gate degree, lookups, copies, table rows. The
class backs skills/constraint-cost/scripts/constraint_count.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

from .r1cs import P_TOY

__all__ = ["Plonkish", "next_pow2"]

Gate = Tuple[int, Callable[[dict, dict], int]]   # (degree, fn(row cells, next row cells) -> field value)


def next_pow2(m: int) -> int:
    return 1 << max(0, (m - 1).bit_length())


@dataclass
class Plonkish:
    """A toy Plonkish table: rows of advice cells, named gates per row, copy constraints, lookups."""
    advice_cols: int
    gates: Dict[str, Gate]
    rows: list = field(default_factory=list)       # (tuple of gate names enabled on the row, {col: value})
    copies: list = field(default_factory=list)     # ((row, col), (row, col)) or ((row, col), ("pub", j))
    lookups: list = field(default_factory=list)    # (row, col, shift): value * shift must be in the table
    table: range = range(0)

    @property
    def max_degree(self) -> int:
        return max(d for d, _ in self.gates.values())

    def failing(self, public: List[int], p: int = P_TOY) -> List[str]:
        """Human-readable list of violated gates / copies / lookups (empty = satisfied)."""
        get = lambda rc: public[rc[1]] if rc[0] == "pub" else self.rows[rc[0]][1][rc[1]]
        bad = []
        for r, (gs, cells) in enumerate(self.rows):
            nxt = self.rows[r + 1][1] if r + 1 < len(self.rows) else {}
            bad += [f"gate {g} @ row {r}" for g in gs if self.gates[g][1](cells, nxt) % p]
        bad += [f"copy {a} = {b}" for a, b in self.copies if (get(a) - get(b)) % p]
        tab = set(self.table)
        bad += [f"lookup ({r}, {col}) x {shift}" for r, col, shift in self.lookups
                if (self.rows[r][1][col] * shift) % p not in tab]
        return bad

    def satisfied(self, public: List[int], p: int = P_TOY) -> bool:
        return not self.failing(public, p)

    def counts(self) -> dict:
        used = len(self.rows)
        height = max(used, len(self.table))     # a fixed table column shares the row space of the circuit
        return {"rows": used, "height": height, "height_pow2": next_pow2(height), "advice_cols": self.advice_cols,
                "fixed_cols": (1 if len(self.table) else 0), "max_degree": self.max_degree,
                "lookups": len(self.lookups), "copies": len(self.copies), "table_rows": len(self.table)}


if __name__ == "__main__":
    # x = a * b on one row, a copied from the public input
    t = Plonkish(3, {"mul": (2, lambda c, _: c["a"] * c["b"] - c["c"])})
    t.rows.append((("mul",), {"a": 3, "b": 4, "c": 12}))
    t.copies.append(((0, "a"), ("pub", 0)))
    assert t.satisfied([3]) and not t.satisfied([5])
    assert t.counts()["height_pow2"] == 1 and t.counts()["max_degree"] == 2
    print("plonkish: OK")
