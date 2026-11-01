# TOY: not secure -- small fields, no zero-knowledge, simulated groups; for reasoning and counting only.
"""cryptomath.zk -- toy proof-system components over small prime fields.

Modules are imported lazily (PEP 562), so ``from cryptomath.zk import r1cs``
loads neither numpy nor sympy; only the Fiat--Shamir and hiding variants import
:mod:`cryptomath.protocols` (which needs sympy), and only when called.

Modules
-------
field      small prime fields (F_17, F_97, Goldilocks), inverses, roots of unity,
           polynomial evaluation and Lagrange interpolation
mle        multilinear extensions: evaluation by folding, eq(x, r) and its table
sumcheck   sum-check prover / verifier (interactive and Fiat--Shamir), a cheating
           prover for empirical soundness checks
merkle     Merkle commitment, single and pruned multi-openings, collision extraction
fri        toy FRI (folding factor, rate, queries) and its proof-size count
kzg        KZG *algebra only*: a simulated group with known discrete logarithms
plonk      permutation argument (grand product) and lookup argument (logUp)
r1cs       R1CS representation, satisfiability, counts
plonkish   Plonkish tables (gates, copies, lookups), satisfiability, counts

Each module's docstring cites where the construction is treated in the
reference books (``[Thaler §...]``, ``[CY24 §...]``).
"""
from __future__ import annotations

import importlib

MODULES = ("field", "mle", "sumcheck", "merkle", "fri", "kzg", "plonk", "r1cs", "plonkish")

__all__ = list(MODULES)


def __getattr__(name: str):
    if name in MODULES:
        mod = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(MODULES))
