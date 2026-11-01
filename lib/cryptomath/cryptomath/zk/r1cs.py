# TOY: not secure -- plain dictionaries and Python ints; for counting constraints and auditing tiny gadgets.
"""Rank-1 constraint systems: representation, satisfiability, counts.

An R1CS instance over F_p is a list of constraints <a, z> * <b, z> = <c, z>
where a, b, c are sparse linear combinations over the variable vector z,
which contains the constant ``one`` = 1, the public inputs and the witness
([Thaler §8.4, Extension from Circuit-SAT to R1CS-SAT]). Linear combinations
are dicts ``{variable name: coefficient}``.

Counts (:meth:`R1CS.counts`) use the conventions of skills/constraint-cost and
CIRCUITS.md: constraints, variables (including ``one``), nonzeros (entries of
A, B, C), max degree 2, no lookups. The same class backs
skills/constraint-cost/scripts/constraint_count.py (builders and closed forms)
and skills/circuit-audit/scripts/toy_circuit_audit.py (exhaustive audit of
small gadgets, using the per-constraint ``tag`` to name what failed).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

__all__ = ["P_TOY", "LC", "R1CS"]

P_TOY = 2 ** 31 - 1     # default field: any prime above the values a toy gadget handles

LC = Dict[str, int]     # linear combination: variable name -> coefficient ("one" is the constant 1)


@dataclass
class R1CS:
    """Constraints <a,z> * <b,z> = <c,z> over F_p; z maps names to field elements, z["one"] = 1."""
    p: int = P_TOY
    public: List[str] = field(default_factory=list)
    witness: List[str] = field(default_factory=list)
    constraints: List[Tuple[LC, LC, LC, str]] = field(default_factory=list)

    def add(self, a: LC, b: LC, c: LC, tag: str = "") -> None:
        self.constraints.append((a, b, c, tag))

    @property
    def variables(self) -> set:
        out = {"one"} | set(self.public) | set(self.witness)
        for a, b, c, _ in self.constraints:
            out.update(a, b, c)
        return out

    def nonzeros(self) -> int:
        return sum(len(a) + len(b) + len(c) for a, b, c, _ in self.constraints)

    def _lc(self, lc: LC, z: dict) -> int:
        return sum(coef * z[v] for v, coef in lc.items()) % self.p

    def failing(self, z: dict) -> List[str]:
        """Tags (or indices, for untagged constraints) of the constraints that z violates."""
        return [tag or str(k) for k, (a, b, c, tag) in enumerate(self.constraints)
                if (self._lc(a, z) * self._lc(b, z) - self._lc(c, z)) % self.p]

    def satisfied(self, z: dict) -> bool:
        return all((self._lc(a, z) * self._lc(b, z) - self._lc(c, z)) % self.p == 0
                   for a, b, c, _ in self.constraints)

    def counts(self) -> dict:
        return {"constraints": len(self.constraints), "variables": len(self.variables),
                "nonzeros": self.nonzeros(), "max_degree": 2, "lookups": 0, "table_rows": 0}

    def matrices(self) -> Tuple[List[str], list, list, list]:
        """(variable order, A, B, C) with rows as {column index: coefficient}; ``one`` is column 0."""
        order = ["one"] + sorted(self.variables - {"one"})
        col = {v: k for k, v in enumerate(order)}
        rows = [[{col[v]: co % self.p for v, co in lc.items()} for lc in (a, b, c)] for a, b, c, _ in self.constraints]
        return order, [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows]


if __name__ == "__main__":
    cs = R1CS(p=97, public=["x"], witness=["b0", "b1"])
    for b in ("b0", "b1"):
        cs.add({b: 1}, {b: 1, "one": -1}, {}, f"bool[{b}]")
    cs.add({"one": 1}, {"b0": 1, "b1": 2}, {"x": 1}, "recompose")
    assert cs.satisfied({"one": 1, "x": 3, "b0": 1, "b1": 1})
    assert cs.failing({"one": 1, "x": 3, "b0": 3, "b1": 0}) == ["bool[b0]"]
    assert cs.counts() == {"constraints": 3, "variables": 4, "nonzeros": 10, "max_degree": 2, "lookups": 0,
                           "table_rows": 0}
    print("r1cs: OK")
