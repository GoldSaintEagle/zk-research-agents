# PIOPs, compilers and arithmetizations

The information-theoretic half of a SNARK and the constraint systems it proves: sum-check and GKR-style interactive proofs (LFKN, Thaler, Libra, Virgo), the IOP model and its compilers (BCS16, RRR16), QAP/linear-PCP SNARKs with Groth16 as the reference point (GGPR, Gro16), universal-SRS SNARKs (Sonic, PLONK), CCS, R1CS IOPs (Aurora, Fractal, Marlin's AHP), AIR/STARK, and sum-check SNARKs (Spartan, HyperPlonk). Entries partly drawn from the bibliographic notes of [CY24 §Bibliographic notes, section:bibliographic-notes] and Thaler's bibliography.

Suggested order: LFKN92 -> GKR15 -> Tha13 -> XZZPS19 -> ZXZS20 (sum-check / GKR line); BCS16 -> RRR16 -> BCRSVW19 -> COS20 -> BBHR19 (IOP / transparent line); GGPR13 -> Gro16 -> MBKM19 -> GWC19 -> CHMMVW20 (linear-PCP / universal-SRS / AHP line); STW23 (CCS, the arithmetization that HyperNova folds); Set20 -> CBBZ23 (multilinear PIOP line).

BibTeX: [`piop-arithmetization.bib`](piop-arithmetization.bib) — 18 entries, checked on 2026-11-01 with `skills/bib-verify/scripts/verify_bib.py`: 16 `VERIFIED` (title, authors, year) through Crossref / DataCite DOIs, 2 ePrint-only papers matched first against the third-party ePrint mirror (eprint.iacr.org refused this machine on that date) and re-checked on 2026-11-03 against eprint.iacr.org itself with `--require-official`: `VERIFIED`. ePrint rows link and cite the official `https://eprint.iacr.org/YYYY/NNNN`; the DOI / ePrint column links the version the entry was verified against. The venue column is informational and was not machine-checked. Re-run the verifier before copying entries into a paper.

| key | DOI / ePrint | year | title | venue | why read |
|---|---|---|---|---|---|
| `LFKN92` | [doi](https://doi.org/10.1145/146585.146605) | 1992 | Algebraic methods for interactive proof systems | J. ACM 1992 | sum-check protocol |
| `GGPR13` | [doi](https://doi.org/10.1007/978-3-642-38348-9_37) | 2013 | Quadratic Span Programs and Succinct NIZKs without PCPs | EUROCRYPT 2013 | QAP/QSP arithmetization |
| `Tha13` | [doi](https://doi.org/10.1007/978-3-642-40084-1_5) | 2013 | Time-Optimal Interactive Proofs for Circuit Evaluation | CRYPTO 2013 | linear-time sum-check / GKR prover |
| `GKR15` | [doi](https://doi.org/10.1145/2699436) | 2015 | Delegating Computation: Interactive Proofs for Muggles | J. ACM 2015 | GKR: layered-circuit interactive proof via sum-check |
| `BCS16` | [doi](https://doi.org/10.1007/978-3-662-53644-5_2) | 2016 | Interactive Oracle Proofs | TCC 2016-B | IOP model + BCS compiler |
| `Gro16` | [doi](https://doi.org/10.1007/978-3-662-49896-5_11) | 2016 | On the Size of Pairing-Based Non-interactive Arguments | EUROCRYPT 2016 | Groth16 reference SNARK |
| `RRR16` | [doi](https://doi.org/10.1145/2897518.2897652) | 2016 | Constant-round interactive proofs for delegating computation | STOC 2016 | IOP-style constant-round proofs |
| `BBHR19` | [doi](https://doi.org/10.1007/978-3-030-26954-8_23) | 2019 | Scalable Zero Knowledge with No Trusted Setup | CRYPTO 2019 | STARK / AIR |
| `BCRSVW19` | [doi](https://doi.org/10.1007/978-3-030-17653-2_4) | 2019 | Aurora: Transparent Succinct Arguments for R1CS | EUROCRYPT 2019 | Aurora: R1CS IOP |
| `XZZPS19` | [doi](https://doi.org/10.1007/978-3-030-26954-8_24) | 2019 | Libra: Succinct Zero-Knowledge Proofs with Optimal Prover Computation | CRYPTO 2019 | Libra: linear-time GKR prover |
| `GWC19` | [ePrint 2019/953](https://eprint.iacr.org/2019/953) | 2019 | PLONK: Permutations over Lagrange-bases for Oecumenical Noninteractive arguments of Knowledge | ePrint | PLONK: Plonkish arithmetization, permutation argument |
| `MBKM19` | [doi](https://doi.org/10.1145/3319535.3339817) | 2019 | Sonic: Zero-Knowledge SNARKs from Linear-Size Universal and Updatable Structured Reference Strings | CCS 2019 | Sonic: first universal updatable-SRS SNARK, PLONK's predecessor |
| `CHMMVW20` | [doi](https://doi.org/10.1007/978-3-030-45721-1_26) | 2020 | Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS | EUROCRYPT 2020 | Marlin: AHP + PCS compiler |
| `COS20` | [doi](https://doi.org/10.1007/978-3-030-45721-1_27) | 2020 | Fractal: Post-quantum and Transparent Recursive Proofs from Holography | EUROCRYPT 2020 | Fractal: holographic IOP, recursion |
| `Set20` | [doi](https://doi.org/10.1007/978-3-030-56877-1_25) | 2020 | Spartan: Efficient and General-Purpose zkSNARKs Without Trusted Setup | CRYPTO 2020 | Spartan: sum-check SNARK for R1CS |
| `ZXZS20` | [doi](https://doi.org/10.1109/sp40000.2020.00052) | 2020 | Transparent Polynomial Delegation and Its Applications to Zero Knowledge Proof | IEEE S&P 2020 | Virgo: transparent GKR + PCS |
| `CBBZ23` | [doi](https://doi.org/10.1007/978-3-031-30617-4_17) | 2023 | HyperPlonk: Plonk with Linear-Time Prover and High-Degree Custom Gates | EUROCRYPT 2023 | HyperPlonk: multilinear PLONK, custom gates |
| `STW23` | [ePrint 2023/552](https://eprint.iacr.org/2023/552) | 2023 | Customizable constraint systems for succinct arguments | ePrint | CCS: one constraint system generalising R1CS, Plonkish and AIR |
