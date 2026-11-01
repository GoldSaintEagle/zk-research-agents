"""Symbolic cost formulas (sympy) and algorithm comparison reports.

* :class:`CostFormula` -- ``{op: sympy expression}`` in named parameters;
  evaluate, add, scale, weight, compare asymptotically, find crossover points.
* :func:`compare` -- run two Python implementations under counters and
  produce a Markdown table (counts, weighted totals, ratio).
* ZK primitive formulas: MSM, NTT, Merkle commit / opening, sum-check, KZG
  commit / open / verify, FRI commit / folding / queries.  Each one is the
  symbolic twin of an integer function in :mod:`cryptomath.costmodel.zkops`
  (sources are cited there); tests check that the two agree.
* Schoolbook vs Karatsuba multiplication as a generic crossover example.

Symbols: ``N`` (size, a power of two), ``b`` (scalar bits), ``c`` (Pippenger
window), ``L`` (Merkle leaves), ``q`` (queries), ``v`` (sum-check variables),
``d`` (degree per variable), ``rho`` (inverse rate).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import sympy as sp

from .counter import (BFLY, DEFAULT_WEIGHTS, GADD, HASH, MSM, MSM_PTS, NTT, PAIR, SC_ROUND, SC_TERM,
                      Counter)

__all__ = ["CostFormula", "compare", "markdown_table", "symbols", "karatsuba_formula", "schoolbook_formula",
           "msm_formula", "ntt_formula", "merkle_formula", "merkle_opening_formula", "sumcheck_formula",
           "kzg_commit_formula", "kzg_open_formula", "kzg_verify_formula", "fri_commit_formula",
           "fri_fold_formula", "fri_query_formula"]


def symbols(names: str):
    """sympy positive symbols, e.g. ``n, d = symbols('n d')``."""
    return sp.symbols(names, positive=True)


@dataclass
class CostFormula:
    terms: Dict[str, sp.Expr] = field(default_factory=dict)
    name: str = ""

    def __add__(self, other: "CostFormula") -> "CostFormula":
        t = dict(self.terms)
        for k, v in other.terms.items():
            t[k] = t.get(k, 0) + v
        return CostFormula(t, f"{self.name}+{other.name}")

    def __mul__(self, c) -> "CostFormula":
        return CostFormula({k: v * c for k, v in self.terms.items()}, self.name)

    __rmul__ = __mul__

    def weighted(self, weights: Optional[Dict[str, float]] = None) -> sp.Expr:
        w = DEFAULT_WEIGHTS if weights is None else weights
        return sp.simplify(sum(sp.nsimplify(w.get(k, 0)) * v for k, v in self.terms.items()))

    def evaluate(self, **params) -> Dict[str, float]:
        subs = {sp.Symbol(k, positive=True): v for k, v in params.items()}
        return {k: float(sp.N(v.subs(subs))) for k, v in self.terms.items()}

    def total(self, weights: Optional[Dict[str, float]] = None, **params) -> float:
        subs = {sp.Symbol(k, positive=True): v for k, v in params.items()}
        return float(sp.N(self.weighted(weights).subs(subs)))

    def leading(self, var: str, weights: Optional[Dict[str, float]] = None) -> sp.Expr:
        """Leading asymptotic term of the weighted cost in ``var`` -> oo."""
        x = sp.Symbol(var, positive=True)
        expr = sp.expand(self.weighted(weights))
        return sp.limit(expr / sp.Order(expr, (x, sp.oo)).expr, x, sp.oo) * sp.Order(expr, (x, sp.oo)).expr

    def crossover(self, other: "CostFormula", var: str, lo: float = 1, hi: float = 1e6,
                  weights: Optional[Dict[str, float]] = None, **fixed) -> Optional[float]:
        """Smallest integer value of ``var`` in [lo, hi] where self becomes cheaper than other."""
        x = sp.Symbol(var, positive=True)
        subs = {sp.Symbol(k, positive=True): v for k, v in fixed.items()}
        diff = sp.lambdify(x, (self.weighted(weights) - other.weighted(weights)).subs(subs), "math")
        v = int(lo)
        while v <= hi:
            if diff(v) < 0:
                return v
            v = v + 1 if v < 64 else int(v * 1.05) + 1
        return None


def markdown_table(rows: Dict[str, Dict[str, float]], columns: Optional[Sequence[str]] = None) -> str:
    """rows: {row_name: {col: value}} -> Markdown table string."""
    cols = list(columns) if columns else sorted({c for r in rows.values() for c in r})
    lines = ["| | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for name, r in rows.items():
        cells = []
        for c in cols:
            v = r.get(c, 0)
            cells.append(f"{v:.4g}" if isinstance(v, float) else str(v))
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def compare(fa: Callable, fb: Callable, *args, names: Tuple[str, str] = ("A", "B"),
            weights: Optional[Dict[str, float]] = None, check_equal: bool = True, **kwargs) -> Dict:
    """Run ``fa(*args)`` and ``fb(*args)`` under counters; return counts + report.

    If ``check_equal`` the two outputs must compare equal (functional
    equivalence is the first thing to screen).
    """
    with Counter(names[0]) as ca:
        ra = fa(*args, **kwargs)
    with Counter(names[1]) as cb:
        rb = fb(*args, **kwargs)
    if check_equal:
        va = getattr(ra, "value", ra)
        vb = getattr(rb, "value", rb)
        try:
            equal = bool(va == vb) if not hasattr(va, "__len__") else list(va) == list(vb)
        except Exception:
            equal = False
    else:
        equal = None
    ta, tb = ca.total(weights), cb.total(weights)
    rows = {names[0]: dict(ca.as_dict(), weighted=ta), names[1]: dict(cb.as_dict(), weighted=tb)}
    return {
        "counts": {names[0]: ca.as_dict(), names[1]: cb.as_dict()},
        "weighted": {names[0]: ta, names[1]: tb},
        "ratio": (ta / tb) if tb else float("inf"),
        "equal_outputs": equal,
        "report": markdown_table(rows),
    }


# ---- ready-made formulas -------------------------------------------------

def _sym(names: str):
    return sp.symbols(names, positive=True)


def schoolbook_formula() -> CostFormula:
    n = sp.Symbol("n", positive=True)
    return CostFormula({"field_mult": n ** 2}, "schoolbook")


def karatsuba_formula() -> CostFormula:
    n = sp.Symbol("n", positive=True)
    return CostFormula({"field_mult": n ** sp.log(3, 2)}, "karatsuba")


def msm_formula() -> CostFormula:
    """Pippenger MSM: ceil(b/c) (N + 2^(c+1)) group additions (c = window)."""
    N, b, c = _sym("N b c")
    return CostFormula({MSM: sp.Integer(1), MSM_PTS: N, GADD: sp.ceiling(b / c) * (N + 2 ** (c + 1))}, "MSM")


def ntt_formula() -> CostFormula:
    """Radix-2 NTT of size N: (N/2) log2 N butterflies."""
    N = sp.Symbol("N", positive=True)
    return CostFormula({NTT: sp.Integer(1), BFLY: N / 2 * sp.log(N, 2)}, "NTT")


def merkle_formula() -> CostFormula:
    """Binary Merkle commitment to L leaves: 2L - 1 hashes."""
    L = sp.Symbol("L", positive=True)
    return CostFormula({HASH: 2 * L - 1}, "Merkle")


def merkle_opening_formula() -> CostFormula:
    """q unpruned openings in a tree of L leaves: q log2 L path nodes (verifier hashes, proof hashes)."""
    L, q = _sym("L q")
    return CostFormula({HASH: q * sp.log(L, 2)}, "Merkle-open")


def sumcheck_formula() -> CostFormula:
    """Sum-check prover over v variables, degree d: v rounds, (d+1)(2^v - 1) summand evaluations."""
    v, d = _sym("v d")
    return CostFormula({SC_ROUND: v, SC_TERM: (d + 1) * (2 ** v - 1)}, "sum-check")


def kzg_commit_formula() -> CostFormula:
    return msm_formula()


def kzg_open_formula() -> CostFormula:
    """Opening = MSM over the N - 1 coefficients of the quotient."""
    N, b, c = _sym("N b c")
    M = N - 1
    return CostFormula({MSM: sp.Integer(1), MSM_PTS: M, GADD: sp.ceiling(b / c) * (M + 2 ** (c + 1))}, "KZG-open")


def kzg_verify_formula() -> CostFormula:
    return CostFormula({PAIR: sp.Integer(2)}, "KZG-verify")


def fri_commit_formula() -> CostFormula:
    """Interpolate (NTT N), extend (NTT rho N), Merkle tree over rho N leaves."""
    N, rho = _sym("N rho")
    return CostFormula({NTT: sp.Integer(2),
                        BFLY: N / 2 * sp.log(N, 2) + rho * N / 2 * sp.log(rho * N, 2),
                        HASH: 2 * rho * N - 1}, "FRI-commit")


def fri_fold_formula() -> CostFormula:
    """Folding layers (factor 2): trees over rho N / 2, ..., 2 leaves, sum_i (2 rho N / 2^i - 1)."""
    N, rho = _sym("N rho")
    D = sp.log(rho * N, 2)
    return CostFormula({HASH: 2 * rho * N - 4 - (D - 1)}, "FRI-fold")


def fri_query_formula() -> CostFormula:
    """Verifier: q unpruned paths in layers of depth D, ..., 1 with D = log2(rho N)."""
    N, rho, q = _sym("N rho q")
    D = sp.log(rho * N, 2)
    return CostFormula({HASH: q * D * (D + 1) / 2}, "FRI-query")
