# baselines/MANIFEST.md (owner: baseline-engineer; skills/baseline-pin)

| baseline | source | pin | build recipe | fairness sign-off |
|---|---|---|---|---|
| **bits arm** (running-sum bit decomposition, Plonkish; strongest bit encoding, IDEAS I3) | `circuits/range_gadgets.py::plonk_bits` | file hash in `results/CODE-SHA256.txt` | none (pure Python); `python3 impl/prove.py --arm bits --k K --n 64` | same prover (`impl/toy_prover.py`), transcript, field, hash, interpreter and process as the lookup arm; same timer scope (prove only, process CPU time); same soundness-level definition (worst-case) — the lookup arm's budget is 3–4 bits lower because of the logUp round (THEORY.md), recorded in DECISIONS D-4 |
| R1CS bit decomposition | `circuits/range_gadgets.py::r1cs_bits` | same | counts only (no R1CS prover here) | **not like-for-like** with Plonkish rows (constraint-cost §1 "same unit across arms"): reported in its own column, never in a ratio with rows (C7) |
| halo2 / plonky3 lookup gadgets | references/baselines/MANIFEST.md rows | not pinned | — | out of scope (DECISIONS D-1): different machine-level PCS, field and soundness level; would need a P4 reproduction first |

Checks done before any number existed (2026-11-02):
- [x] both arms built by the same builder module and proven by the same prover (no arm-specific fast path);
- [x] the vanilla 3-wire bit encoding (n(2k − 1) rows) is **not** used as the baseline: it would inflate the gain;
- [x] published-number reproduction: n/a (our own textbook baseline; waiver in STATE.md, D-1/D-4).
