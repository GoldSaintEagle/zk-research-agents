"""cryptomath -- toy-scale cryptography mathematics for research screening.

Subpackages are imported lazily (PEP 562 ``__getattr__``), so a missing or
broken optional subpackage never breaks ``import cryptomath``::

    import cryptomath
    cryptomath.algebra.cyclotomic_poly(12)
    cryptomath.available()          # -> {'algebra': True, 'ec': False, ...}

Subpackages
-----------
algebra    prime and extension fields, polynomials, roots of unity, NTT
costmodel  abstract operation counting; ZK primitive counts (MSM, NTT, Merkle,
           sum-check, PCS commit/open) as code and as sympy formulas
symmetric  arithmetization-oriented primitive costs (Poseidon, MiMC, ...), GF(2^n)
protocols  hash / Pedersen commitments, Fiat--Shamir transcript, Schnorr
ec         small prime-field elliptic curves, toy groups, generic DLP

Everything here is for experimentation and teaching. Nothing is constant-time
and every proof-system component is insecure by construction (small fields,
no zero-knowledge, simulated groups).
"""
from __future__ import annotations

import importlib

__version__ = "0.1.0"

SUBPACKAGES = ("algebra", "costmodel", "symmetric", "protocols", "ec")

__all__ = list(SUBPACKAGES) + ["available", "__version__"]


def __getattr__(name: str):
    if name in SUBPACKAGES:
        mod = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def available() -> dict:
    """Return ``{subpackage: importable?}`` without raising."""
    out = {}
    for name in SUBPACKAGES:
        try:
            importlib.import_module(f"{__name__}.{name}")
            out[name] = True
        except Exception:  # pragma: no cover - depends on install state
            out[name] = False
    return out


def __dir__():
    return sorted(set(globals()) | set(SUBPACKAGES))
