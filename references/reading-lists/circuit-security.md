# Circuit correctness and under-constrained bugs

Whether the constraint system actually enforces the intended computation: the circuit languages and compilers where bugs are introduced (Circom, CirC), finite-field SMT reasoning as the engine for circuit verification (OKTB23, HKK23), compiler soundness (finite-field blasting, OWBB23), static detection of under-constrained circuits (Picus/QED², PCWRVMCG23; consistency checking, SPD25), refinement-type certification (Coda, LKLTWSPM24), theorem-prover verification of circuits (ACL2, CMS23), testing and fuzzing of circuits and ZK compilers (MTZK, zkFuzz, HIWC25, CAD25), and a case study on how far a machine-checked ZK implementation can be trusted (OPS25). The SoK by Chaliasos et al. (USENIX Security 2024), ZKAP (USENIX Security 2024), Ecne, Circomspect and the Leo verification paper are left out because no DOI could be verified for them.

Suggested order: BIMRB23 -> OBW22 (languages and compilers); OKTB23 -> HKK23 -> OWBB23 (finite-field SMT, compiler soundness); PCWRVMCG23 -> SPD25 -> LKLTWSPM24 -> CMS23 (verification of circuits); XLPW25 -> CAD25 -> HIWC25 -> TKJY26 (testing and fuzzing); OPS25 (verified implementations).

BibTeX: [`circuit-security.bib`](circuit-security.bib) — 14 entries, verified on 2026-11-01 through Crossref / DataCite DOIs with skills/bib-verify/scripts/verify_bib.py; ePrint ids omitted because eprint.iacr.org refused this machine on that date — add `eprint=` after an ePrint-reachable re-run. The venue column is informational and was not machine-checked. Re-run the verifier before copying entries into a paper.

| key | DOI | year | title | venue | why read |
|---|---|---|---|---|---|
| `OBW22` | [doi](https://doi.org/10.1109/sp46214.2022.9833782) | 2022 | CirC: Compiler infrastructure for proof systems, software verification, and more | IEEE S&P 2022 | shared IR for ZK and SMT |
| `BIMRB23` | [doi](https://doi.org/10.1109/tdsc.2022.3232813) | 2023 | Circom: A Circuit Description Language for Building Zero-Knowledge Applications | IEEE TDSC 2023 | Circom semantics, witness vs. constraints |
| `PCWRVMCG23` | [doi](https://doi.org/10.1145/3591282) | 2023 | Automated Detection of Under-Constrained Circuits in Zero-Knowledge Proofs | PACMPL (PLDI 2023) | Picus / QED² |
| `OKTB23` | [doi](https://doi.org/10.1007/978-3-031-37703-7_8) | 2023 | Satisfiability Modulo Finite Fields | CAV 2023 | finite-field SMT |
| `OWBB23` | [doi](https://doi.org/10.1007/978-3-031-37709-9_8) | 2023 | Bounded Verification for Finite-Field-Blasting | CAV 2023 (FMSD 2025) | compiler-pass soundness |
| `HKK23` | [doi](https://doi.org/10.29007/4n6w) | 2023 | SMT Solving over Finite Field Arithmetic | LPAR 2023 | finite-field SMT |
| `CMS23` | [doi](https://doi.org/10.4204/eptcs.393.9) | 2023 | Formal Verification of Zero-Knowledge Circuits | EPTCS (ACL2 Workshop 2023) | theorem-prover verification of R1CS |
| `LKLTWSPM24` | [doi](https://doi.org/10.1109/sp54263.2024.00078) | 2024 | Certifying Zero-Knowledge Circuits with Refinement Types | IEEE S&P 2024 | Coda |
| `XLPW25` | [doi](https://doi.org/10.14722/ndss.2025.230530) | 2025 | MTZK: Testing and Exploring Bugs in Zero-Knowledge (ZK) Compilers | NDSS 2025 | metamorphic testing of ZK compilers |
| `SPD25` | [doi](https://doi.org/10.1007/978-3-031-98668-0_16) | 2025 | Automated Verification of Consistency in Zero-Knowledge Proof Circuits | CAV 2025 | witness/constraint consistency |
| `HIWC25` | [doi](https://doi.org/10.1145/3719027.3744791) | 2025 | Fuzzing Processing Pipelines for Zero-Knowledge Circuits | CCS 2025 | fuzzing ZK toolchains |
| `CAD25` | [doi](https://doi.org/10.1145/3713081.3731718) | 2025 | Towards Fuzzing Zero-Knowledge Proof Circuits (Short Paper) | ISSTA Companion 2025 | circuit fuzzing |
| `OPS25` | [doi](https://doi.org/10.62056/a0wa0lmol) | 2025 | Who Verifies the Verifiers? | IACR CiC 2025 | how far a machine-checked ZK implementation can be trusted |
| `TKJY26` | [doi](https://doi.org/10.1109/sp63933.2026.00049) | 2026 | zkFuzz: Foundation and Framework for Effective Fuzzing of Zero-Knowledge Circuits | IEEE S&P 2026 | fuzzing framework for circuits |
