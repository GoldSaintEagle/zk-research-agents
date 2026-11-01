"""cryptomath.protocols -- commitments and Fiat--Shamir helpers.

# TOY: not secure -- small-parameter, non-constant-time code for checking correctness
# and for building toy proof systems (see cryptomath.zk).

Modules
-------
commitments     hash commitment, Pedersen commitment
fiat_shamir     Transcript (domain-separated, length-prefixed absorb / squeeze),
                Schnorr sigma protocol (+ NIZK, simulator, extractor)

Quick start::

    from cryptomath.protocols import Transcript
    t = Transcript(b"toy-proof")
    t.append(b"commitment", b"...")
    t.challenge_scalar(b"r", 97)
"""
from .commitments import hash_commit, hash_verify, Pedersen
from .fiat_shamir import (Transcript, SchnorrProver, schnorr_verify, schnorr_simulate,
                          schnorr_nizk_prove, schnorr_nizk_verify, schnorr_extract)

__all__ = [n for n in dir() if not n.startswith("_")]
