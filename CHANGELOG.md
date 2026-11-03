# Changelog

## 0.2.0 — 2026-11-03 (ZK fork)

This is the first release of the ZK-only fork of
[crypto-research-agents](https://github.com/acprk/crypto-research-agents), forked from upstream commit `bfe2303`
(2026-09-25). The process is unchanged: blackboard files, falsify-first, the evidence ledger and the P0–P8 gates.
The domain content is now ZK only.

### Agents (12 → 13)
- New: **prover-engineer**, which owns `impl/`, and **circuit-engineer**, which owns `circuits/` and `CIRCUITS.md`.
- math-librarian is merged into **lit-scout**, which now owns `textbook-index` and `MATH-REFS.md`.
- The other nine agents are rewritten for ZK. The builders' circuit and Fiat–Shamir self-audits are always re-run
  independently by the falsifier, and the falsifier recomputes every soundness budget.

### Skills (28 → 34)
- New: soundness-budget, zk-definitions, piop-pcs-compile, fiat-shamir-audit, circuit-audit, constraint-cost,
  prover-cost-model.
- Rewritten for ZK: falsify, sage-check, idea-mining-loop, baseline-pin, bench-protocol, venue-calibration,
  paper-playbook, paper-figures, mock-review, lean-bridge.
- ZK checks and examples added: anonymize-check (on-chain addresses, package metadata, ZK allow-list),
  figure-harvest, polish-writing (ZK term protection), abstract-craft, phase-gate, lit-matrix, eprint-search
  (grey literature, rate limit, mirror fallback), bib-verify (URL sources), technique-overview,
  related-work-writing, experiments-writing, artifact-pack, textbook-index.
- Removed: param-estimation, replaced by soundness-budget.

### Commands
- New: `/cra-soundness`, `/cra-circuit-audit`, `/cra-fs-audit`.

### Libraries
- `lib/cryptomath`:
  - new `zk/` module with toy components: small fields, MLE, sum-check, Merkle, FRI, KZG algebra, PLONK
    permutation and logUp, R1CS and Plonkish;
  - ZK cost models;
  - removed: the FHE and lattice modules, the symmetric-cipher modules apart from AO-primitive costs and GF(2^n),
    and the FHE slot-layout helper.
- `lib/bench` (crbench):
  - new ZK parsers: snarkjs, rapidsnark, circom, gnark, nargo, RISC Zero, SP1;
  - removed: the HElib, OpenFHE, lattice-estimator and MP-SPDZ parsers;
  - `audit-tex` now understands constraints, rows, gas, cycles, kB and bits.

### References
- Chiesa–Yogev, *Building Cryptographic Proofs from Hash Functions*, pinned at commit `305fa3d`.
- Thaler, *Proofs, Arguments, and Zero-Knowledge*, pinned by PDF sha256.
- Both books are fetched locally and never committed. The repo keeps its own chapter maps and a glossary, and
  `scripts/check_book_refs.py` validates every citation against the pinned versions.
- Eight ZK reading lists with 139 entries, all verified against official sources.
- A baseline MANIFEST of 25 ZK libraries.

### Workflows
- falsify-round now judges a claim with no valid votes as `open`, where it used to say `survived`. Its lenses are
  ZK-specific, and claims about circuits get an extra circuit-audit vote.
- The P3–P6 gates add four requirements:
  - a soundness budget table;
  - sign-off that baselines run at equal soundness;
  - verified proofs in every timed run;
  - passing Fiat–Shamir and circuit audits.

### Case study
- `case-study/toy-rangecheck` replaces the TFHE case. It compares logUp with bit-decomposition range checks over
  Goldilocks and runs P0–P8 end to end. The falsifier catches a planted under-constrained limb and an unplanted
  Fiat–Shamir binding flaw.

### Project
- Renamed to zk-research-agents. `LICENSE` keeps the upstream copyright notice.
- Added `docs/NEEDS-VERIFICATION.md`, which collects every item still waiting for a human check.
